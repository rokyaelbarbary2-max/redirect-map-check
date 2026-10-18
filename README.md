# redirect-map-check

After a URL migration (new CMS, new folder structure, `/cro` → `/service/cro`), the redirect map is the one artefact that decides whether rankings and backlinks survive. This script checks the live site against that map, one row at a time.

For each `old,new` pair:

- the old URL must answer a **permanent** redirect (`301` or `308`) in **one hop**,
- the `Location` header must be exactly the new URL,
- the new URL must answer `200` and must not redirect again.

## Usage

```bash
python3 redirect_map_check.py redirects.csv --base https://example.com
```

`redirects.csv`:

```csv
old,new
/cro,/service/cro
/seo,/service/seo
/ai-automation,/service/ai-automation
```

Output:

```
OK   https://example.com/seo -> https://example.com/service/seo
FAIL https://example.com/cro -> https://example.com/service/cro  | old answers 404, expected 301/308
FAIL https://example.com/ai-automation -> https://example.com/service/ai-automation  | old answers 404, expected 301/308

1/3 rows pass
```

The exit code is `1` if any row fails. Run it right after the deploy that ships the redirects, and again a week later.

## Why one hop and permanent

Temporary redirects (`302`/`307`) and chains of several hops are where link equity and crawl budget leak. A `200` at the old URL is worse: the old page is still there, and there are now two versions of it. The check is strict on purpose.

## Notes

- Paths or absolute URLs both work. `--base` is prepended to paths.
- Query strings are compared exactly. Normalise your map first if your server drops them.
- Python 3.8+ standard library only.

Maintained by [Gorilla Vibe](https://thegorillavibe.com/service/web-platform-development) for migrations and replatforming projects.

## License

MIT
