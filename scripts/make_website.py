#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT_DIR / "templates"

INCLUDE_RE = re.compile(r"\{\{\s*include:\s*([a-zA-Z0-9_./-]+)\s*\}\}")
VAR_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


def _render_template(path: Path, context: dict[str, str], stack: tuple[Path, ...] = ()) -> str:
    if path in stack:
        chain = " -> ".join(str(p.relative_to(TEMPLATES_DIR)) for p in (*stack, path))
        raise RuntimeError(f"Template include cycle detected: {chain}")

    text = path.read_text()

    def include_replacer(match: re.Match[str]) -> str:
        include_rel = match.group(1)
        include_path = TEMPLATES_DIR / include_rel
        if not include_path.exists():
            raise FileNotFoundError(f"Missing included template: {include_path}")
        return _render_template(include_path, context, (*stack, path))

    text = INCLUDE_RE.sub(include_replacer, text)

    def var_replacer(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in context:
            raise KeyError(f"Missing template variable '{key}' for {path}")
        return context[key]

    return VAR_RE.sub(var_replacer, text)


def _page_context(
    *,
    asset_prefix: str,
    page_title: str,
    page_description: str,
    current: str,
) -> dict[str, str]:
    def current_attrs(name: str) -> tuple[str, str]:
        if name == current:
            return ' aria-current="page"', " w--current"
        return "", ""

    nav_brand_aria, nav_brand_current_class = current_attrs("home")
    nav_home_aria, nav_home_current_class = current_attrs("home")
    nav_motorists_aria, nav_motorists_current_class = current_attrs("motorists")
    nav_law_aria, nav_law_current_class = current_attrs("law")

    footer_brand_aria, footer_brand_current_class = current_attrs("home")
    footer_home_aria, footer_home_current_class = current_attrs("home")
    footer_motorists_aria, footer_motorists_current_class = current_attrs("motorists")
    footer_law_aria, footer_law_current_class = current_attrs("law")

    return {
        "asset_prefix": asset_prefix,
        "page_title": page_title,
        "page_description": page_description,
        "page_og_title": page_title,
        "page_og_description": page_description,
        "page_twitter_title": page_title,
        "page_twitter_description": page_description,
        "nav_brand_aria": nav_brand_aria,
        "nav_brand_current_class": nav_brand_current_class,
        "nav_home_aria": nav_home_aria,
        "nav_home_current_class": nav_home_current_class,
        "nav_motorists_aria": nav_motorists_aria,
        "nav_motorists_current_class": nav_motorists_current_class,
        "nav_law_aria": nav_law_aria,
        "nav_law_current_class": nav_law_current_class,
        "footer_brand_aria": footer_brand_aria,
        "footer_brand_current_class": footer_brand_current_class,
        "footer_home_aria": footer_home_aria,
        "footer_home_current_class": footer_home_current_class,
        "footer_motorists_aria": footer_motorists_aria,
        "footer_motorists_current_class": footer_motorists_current_class,
        "footer_law_aria": footer_law_aria,
        "footer_law_current_class": footer_law_current_class,
    }


def main() -> None:
    pages = [
        {
            "template": TEMPLATES_DIR / "pages/home.html",
            "output": ROOT_DIR / "index.html",
            "context": _page_context(
                asset_prefix="",
                page_title="Traafik - Traffic Stops Reimagined",
                page_description=(
                    "Traafik's patented enterprise software represents a game-changing leap "
                    "forward in technology, with unprecedented digital interaction between "
                    "Motorists and Law Enforcement."
                ),
                current="home",
            ),
        },
        {
            "template": TEMPLATES_DIR / "pages/motorists.html",
            "output": ROOT_DIR / "motorists/index.html",
            "context": _page_context(
                asset_prefix="../",
                page_title="Traafik - Motorist",
                page_description=(
                    "Police agencies need a better approach to ensuring the safety of "
                    "citizens during routine traffic stops. Digital interaction."
                ),
                current="motorists",
            ),
        },
        {
            "template": TEMPLATES_DIR / "pages/law_enforcement.html",
            "output": ROOT_DIR / "law-enforcement/index.html",
            "context": _page_context(
                asset_prefix="../",
                page_title="Traafik - Law Enforcement",
                page_description="Smarter Technology for Law Enforcement",
                current="law",
            ),
        },
    ]

    for page in pages:
        rendered = _render_template(page["template"], page["context"]).rstrip() + "\n"
        page["output"].write_text(rendered)
        rel_out = page["output"].relative_to(ROOT_DIR)
        rel_tpl = page["template"].relative_to(ROOT_DIR)
        print(f"Rendered {rel_out} from {rel_tpl}")


if __name__ == "__main__":
    main()
