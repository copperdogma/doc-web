from doc_web.env import CHILD_KEY_BY_PROVIDER, DOC_WEB_KEY_BY_PROVIDER, build_child_env


def test_build_child_env_maps_doc_web_moonshot_key(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DOC_WEB_MOONSHOT_API_KEY=moonshot-key\n")
    monkeypatch.delenv("MOONSHOT_API_KEY", raising=False)

    env = build_child_env(env_file=env_file)

    assert env[DOC_WEB_KEY_BY_PROVIDER["moonshot"]] == "moonshot-key"
    assert env[CHILD_KEY_BY_PROVIDER["moonshot"]] == "moonshot-key"


def test_build_child_env_respects_doc_web_env_file_override(monkeypatch, tmp_path):
    env_file = tmp_path / ".env.main"
    env_file.write_text("DOC_WEB_MOONSHOT_API_KEY=override-key\n")
    monkeypatch.setenv("DOC_WEB_ENV_FILE", str(env_file))
    monkeypatch.delenv("MOONSHOT_API_KEY", raising=False)

    env = build_child_env()

    assert env[CHILD_KEY_BY_PROVIDER["moonshot"]] == "override-key"
