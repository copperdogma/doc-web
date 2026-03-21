from __future__ import annotations

from functools import lru_cache
from typing import Any, ClassVar

from docling_plugins.onward_table_structure_plugin import (
    SUMMARY_LABELS,
    extract_family_labels,
    has_combined_boy_girl_header,
    is_generation_context_text,
    normalize_text,
)

COLUMN_HEADER_MARKERS = {"NAME", "BORN", "MARRIED", "SPOUSE", "BOY", "GIRL", "DIED"}


def is_genealogy_marker_text(text: str | None) -> bool:
    normalized = normalize_text(text)
    if not normalized:
        return False
    upper = normalized.upper()
    if any(label in upper for label in SUMMARY_LABELS):
        return False
    if upper in COLUMN_HEADER_MARKERS:
        return True
    if extract_family_labels(normalized):
        return True
    if has_combined_boy_girl_header(normalized):
        return True
    return is_generation_context_text(normalized)


def page_supports_genealogy_merge(
    *,
    table_cluster_count: int,
    marker_hits: int,
    has_summary_labels: bool,
) -> bool:
    if has_summary_labels or table_cluster_count == 0:
        return False
    if table_cluster_count >= 2:
        return marker_hits >= 1
    return marker_hits >= 2


@lru_cache(maxsize=1)
def _load_docling_types() -> tuple[type[Any], type[Any], type[Any], type[Any], Any]:
    from typing import Type

    from docling.datamodel.base_models import Cluster, LayoutPrediction, Page
    from docling.datamodel.document import ConversionResult
    from docling.datamodel.layout_model_specs import DOCLING_LAYOUT_HERON, LayoutModelConfig
    from docling.datamodel.pipeline_options import BaseLayoutOptions, LayoutOptions
    from docling.models.base_layout_model import BaseLayoutModel
    from docling.models.stages.layout.layout_model import LayoutModel
    from docling_core.types.doc import BoundingBox, DocItemLabel

    class OnwardLayoutOptions(BaseLayoutOptions):
        kind: ClassVar[str] = "onward_layout_v1"
        merge_genealogy_pages: bool = True
        model_spec: LayoutModelConfig = DOCLING_LAYOUT_HERON
        delegate_create_orphan_clusters: bool = True

    table_labels = {DocItemLabel.TABLE, DocItemLabel.DOCUMENT_INDEX}
    absorbable_labels = table_labels.union(
        {
            DocItemLabel.TEXT,
            DocItemLabel.SECTION_HEADER,
            DocItemLabel.TITLE,
            DocItemLabel.LIST_ITEM,
        }
    )

    def _cluster_texts(cluster: Cluster) -> list[str]:
        texts: list[str] = []
        for cell in getattr(cluster, "cells", []) or []:
            normalized = normalize_text(getattr(cell, "text", None))
            if normalized:
                texts.append(normalized)
        return texts

    def _cluster_has_summary_label(cluster: Cluster) -> bool:
        return any(
            summary_label in text.upper()
            for text in _cluster_texts(cluster)
            for summary_label in SUMMARY_LABELS
        )

    def _cluster_has_genealogy_marker(cluster: Cluster) -> bool:
        return any(is_genealogy_marker_text(text) for text in _cluster_texts(cluster))

    def _cell_in_bbox(cell: Any, bbox: BoundingBox) -> bool:
        cell_bbox = cell.rect.to_bounding_box()
        return cell_bbox.get_intersection_bbox(bbox) is not None

    def _build_genealogy_merge(
        page: Page,
        prediction: LayoutPrediction,
        options: OnwardLayoutOptions,
    ) -> tuple[Cluster, set[int]] | None:
        if not options.merge_genealogy_pages:
            return None

        table_clusters = [
            cluster
            for cluster in prediction.clusters
            if cluster.label in table_labels
        ]
        if not table_clusters:
            return None

        marker_clusters = [
            cluster
            for cluster in prediction.clusters
            if cluster.label in absorbable_labels
            and cluster.label not in table_labels
            and _cluster_has_genealogy_marker(cluster)
        ]
        marker_hits = sum(1 for cluster in table_clusters if _cluster_has_genealogy_marker(cluster))
        marker_hits += len(marker_clusters)
        has_summary_labels = any(
            _cluster_has_summary_label(cluster) for cluster in prediction.clusters
        )
        if not page_supports_genealogy_merge(
            table_cluster_count=len(table_clusters),
            marker_hits=marker_hits,
            has_summary_labels=has_summary_labels,
        ):
            return None

        candidate_clusters = list(table_clusters) + marker_clusters
        merged_bbox = BoundingBox.enclosing_bbox([cluster.bbox for cluster in candidate_clusters])
        absorbed_ids = {cluster.id for cluster in candidate_clusters}

        for cluster in prediction.clusters:
            if cluster.id in absorbed_ids or cluster.label not in absorbable_labels:
                continue
            if _cluster_has_summary_label(cluster):
                continue
            if cluster.bbox.get_intersection_bbox(merged_bbox) is None:
                continue
            if cluster.bbox.intersection_over_self(merged_bbox) >= 0.6:
                candidate_clusters.append(cluster)
                absorbed_ids.add(cluster.id)

        merged_bbox = BoundingBox.enclosing_bbox([cluster.bbox for cluster in candidate_clusters])
        merged_cells = [cell for cell in page.cells if _cell_in_bbox(cell, merged_bbox)]
        if not merged_cells:
            merged_cells = [
                cell
                for cluster in candidate_clusters
                for cell in getattr(cluster, "cells", []) or []
            ]

        merged_cluster = min(table_clusters, key=lambda cluster: cluster.id).model_copy(
            update={
                "bbox": merged_bbox,
                "cells": merged_cells,
                "confidence": max(cluster.confidence for cluster in candidate_clusters),
                "label": DocItemLabel.TABLE,
            }
        )
        return merged_cluster, absorbed_ids

    def _rewrite_prediction(
        page: Page,
        prediction: LayoutPrediction,
        options: OnwardLayoutOptions,
    ) -> LayoutPrediction:
        merged = _build_genealogy_merge(page, prediction, options)
        if merged is None:
            return prediction

        merged_cluster, absorbed_ids = merged
        final_clusters = [
            cluster for cluster in prediction.clusters if cluster.id not in absorbed_ids
        ]
        final_clusters.append(merged_cluster)
        final_clusters.sort(key=lambda cluster: cluster.id)
        return prediction.model_copy(update={"clusters": final_clusters})

    class OnwardLayoutModel(BaseLayoutModel):
        def __init__(
            self,
            artifacts_path,
            accelerator_options,
            options: OnwardLayoutOptions,
            enable_remote_services: bool = False,
        ):
            self.options = options
            delegate_options = LayoutOptions(
                keep_empty_clusters=options.keep_empty_clusters,
                skip_cell_assignment=options.skip_cell_assignment,
                create_orphan_clusters=options.delegate_create_orphan_clusters,
                model_spec=options.model_spec,
            )
            self.delegate = LayoutModel(
                artifacts_path=artifacts_path,
                accelerator_options=accelerator_options,
                options=delegate_options,
                enable_remote_services=enable_remote_services,
            )

        @classmethod
        def get_options_type(cls) -> Type[OnwardLayoutOptions]:
            return OnwardLayoutOptions

        def predict_layout(
            self,
            conv_res: ConversionResult,
            pages,
        ):
            pages = list(pages)
            predictions = self.delegate.predict_layout(conv_res, pages)
            return [
                _rewrite_prediction(page, prediction, self.options)
                for page, prediction in zip(pages, predictions)
            ]

    return OnwardLayoutOptions, OnwardLayoutModel, LayoutOptions, LayoutModel, DocItemLabel


def build_layout_options():
    options_type, *_ = _load_docling_types()
    return options_type()


def layout_engines():
    _, model_type, *_ = _load_docling_types()
    return {"layout_engines": [model_type]}
