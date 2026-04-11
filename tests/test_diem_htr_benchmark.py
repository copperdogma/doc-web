from scripts.spikes.diem_htr_benchmark import (
    PAGE_SEPARATOR,
    STORY212_SLICE,
    _build_eval_env,
    build_parser,
    build_story212_transcript,
    classify_geometry,
    extract_alto_lines,
    extract_page_lines,
    should_retry_transient_eval_failure,
)


def test_extract_page_lines_respects_region_reading_order():
    page_xml = """
    <PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15">
      <Page imageFilename="page.jpg" imageWidth="100" imageHeight="100">
        <ReadingOrder>
          <OrderedGroup id="ro">
            <RegionRefIndexed index="1" regionRef="r2" />
            <RegionRefIndexed index="0" regionRef="r1" />
          </OrderedGroup>
        </ReadingOrder>
        <TextRegion id="r1">
          <TextLine id="l1"><TextEquiv><Unicode>first region line</Unicode></TextEquiv></TextLine>
        </TextRegion>
        <TextRegion id="r2">
          <TextLine id="l2"><TextEquiv><Unicode>second region line</Unicode></TextEquiv></TextLine>
        </TextRegion>
      </Page>
    </PcGts>
    """

    assert extract_page_lines(page_xml) == ["first region line", "second region line"]


def test_extract_alto_lines_joins_string_content_in_order():
    alto_xml = """
    <alto xmlns="http://www.loc.gov/standards/alto/ns-v4#">
      <Layout>
        <Page WIDTH="100" HEIGHT="100">
          <PrintSpace>
            <TextBlock>
              <TextLine>
                <String CONTENT="Anno"/>
                <String CONTENT="1758"/>
              </TextLine>
              <TextLine>
                <String CONTENT="Dom:"/>
                <String CONTENT="Trinitatis"/>
              </TextLine>
            </TextBlock>
          </PrintSpace>
        </Page>
      </Layout>
    </alto>
    """

    assert extract_alto_lines(alto_xml) == ["Anno 1758", "Dom: Trinitatis"]


def test_build_story212_transcript_uses_repo_page_separator():
    transcript = build_story212_transcript([["page one line"], ["page two line"]])

    assert PAGE_SEPARATOR in transcript
    assert transcript.strip().startswith("page one line")
    assert transcript.strip().endswith("page two line")


def test_classify_geometry_distinguishes_spread_shapes():
    assert classify_geometry(3500, 2200) == "landscape-spread"
    assert classify_geometry(1700, 2600) == "portrait-spread"
    assert classify_geometry(2500, 2400) == "near-square-spread"


def test_story212_slice_is_small_unique_and_visually_two_page():
    ids = [(page.doc_id, page.sequence) for page in STORY212_SLICE]

    assert len(STORY212_SLICE) == 3
    assert len(ids) == len(set(ids))
    assert all(page.physical_page_count == 2 for page in STORY212_SLICE)


def test_retry_detector_only_matches_transient_gemini_capacity_errors():
    assert should_retry_transient_eval_failure(
        "",
        "503 UNAVAILABLE ... currently experiencing high demand",
    )
    assert not should_retry_transient_eval_failure("", "OCR failed because the transcript path is missing")


def test_build_eval_env_prefers_gemini_key_when_both_google_env_vars_exist(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key")

    env = _build_eval_env()

    assert env["GEMINI_API_KEY"] == "gem-key"
    assert "GOOGLE_API_KEY" not in env
    assert env["PYTHONPATH"]


def test_build_parser_defaults_to_image_only_mode():
    parser = build_parser()

    args = parser.parse_args([])

    assert args.include_pdf is False
    assert args.max_attempts == 2
