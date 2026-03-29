from modules.intake.intake_plan_utils import choose_maintained_recipe


def _plan(
    *,
    input_kind: str,
    has_extractable_text: bool | None = None,
    book_type: str = "other",
    signals: list[str] | None = None,
    tile_count: int = 0,
):
    return {
        "book_type": book_type,
        "signals": signals or [],
        "meta": {
            "summary": {
                "tile_count": tile_count,
            },
            "source_input": {
                "input_kind": input_kind,
                "has_extractable_text": has_extractable_text,
            },
        },
    }


def test_choose_maintained_recipe_keeps_image_directory_lane():
    assert choose_maintained_recipe(_plan(input_kind="images_dir")) == "configs/recipes/recipe-images-ocr-html-mvp.yaml"


def test_choose_maintained_recipe_keeps_proven_born_digital_cyoa_lane():
    assert (
        choose_maintained_recipe(
            _plan(
                input_kind="pdf",
                has_extractable_text=True,
                book_type="cyoa",
                tile_count=3,
            )
        )
        == "configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml"
    )


def test_choose_maintained_recipe_withholds_short_flat_born_digital_pdf():
    assert (
        choose_maintained_recipe(
            _plan(
                input_kind="pdf",
                has_extractable_text=True,
                book_type="other",
                tile_count=2,
            )
        )
        is None
    )


def test_choose_maintained_recipe_withholds_short_scanned_prose_pdf():
    assert (
        choose_maintained_recipe(
            _plan(
                input_kind="pdf",
                has_extractable_text=False,
                book_type="novel",
                tile_count=4,
            )
        )
        is None
    )


def test_choose_maintained_recipe_keeps_structured_scanned_pdf_lane():
    assert (
        choose_maintained_recipe(
            _plan(
                input_kind="pdf",
                has_extractable_text=False,
                book_type="other",
                signals=["tables", "images"],
                tile_count=6,
            )
        )
        == "configs/recipes/recipe-pdf-ocr-html-mvp.yaml"
    )
