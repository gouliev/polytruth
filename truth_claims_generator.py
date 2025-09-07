# ──────────────────────────────────────────────────────────────────────────────
#  TRUE-STATEMENT GENERATOR  ·  MindBugs Discovery
# ──────────────────────────────────────────────────────────────────────────────
#
#  • Reads every FALSE claim in original dataset
#  • Prompts GPT-3.5-turbo and 4o for a short, correct statement in the same language
#  • Streams triples  (false , true , citation)  into  false_true_pairs.csv#
#  pip install --upgrade "openai>=1.0" backoff pandas packaging langcodes
# ──────────────────────────────────────────────────────────────────────────────
import os, csv, time, sys
import pandas as pd, backoff, langcodes, packaging.version as pv
import openai

# ╭──────────────────────────────╮
# │ 1 •  API KEY                 │
# ╰──────────────────────────────╯
if not os.getenv("OPENAI_API_KEY"):
    sys.exit("⛔  export OPENAI_API_KEY before running.")
openai.api_key = os.getenv("OPENAI_API_KEY")

# ╭──────────────────────────────╮
# │ 2 •  CONFIGURATION           │
# ╰──────────────────────────────╯
SRC_CSV  = "all_data_for_pub_clean2.csv"
OUT_CSV  = "false_true_pairs.csv"
MODEL    = "gpt-3.5-turbo"
BATCH_SZ = 10
MAX_TOK  = 96
SLEEP    = 4             

# ╭──────────────────────────────╮
# │ 3 •  HANDLE BOTH CLIENT VERS │
# ╰──────────────────────────────╯
LEGACY = pv.parse(openai.__version__) < pv.parse("1.0.0")
if LEGACY:
    from openai.error import RateLimitError, APIError, Timeout
else:
    RateLimitError = openai.RateLimitError
    APIError       = openai.APIError
    Timeout        = (openai.APITimeoutError
                      if hasattr(openai, "APITimeoutError")
                      else openai.APIConnectionError)

# ╭──────────────────────────────╮
# │ 4 •  LOAD FALSE CLAIMS       │
# ╰──────────────────────────────╯
df = (pd.read_csv(SRC_CSV)
        .drop(columns=["Unnamed: 0"], errors="ignore")
        .rename(columns={"statement": "false_statement"}))

if "languages" not in df.columns:
    sys.exit("⛔  CSV must contain a 'languages' column (ISO code or name).")

records = df[["false_statement", "languages"]].astype(str).values.tolist()

# ╭──────────────────────────────╮
# │ 5 •  RESUME SUPPORT          │
# ╰──────────────────────────────╯
done = 0
if os.path.isfile(OUT_CSV):
    done = sum(1 for _ in open(OUT_CSV, encoding="utf-8")) - 1
    print(f"↻  Resuming at row {done}")
else:
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["false_statement", "true_statement", "citation"])

# ╭──────────────────────────────╮
# │ 6 •  LANGUAGE NORMALISATION  │
# ╰──────────────────────────────╯
def normalise_lang(raw: str) -> str:
    """
    Accept ISO tag ('es'), list-like \"['es']\", or name ('spanish').
    Return human name capitalised; default 'English' on failure.
    """
    txt = raw.lower().strip().lstrip("['").rstrip("']").strip()
    try:
        return langcodes.get(txt).language_name().capitalize()
    except (langcodes.LanguageTagError, LookupError):
        try:
            iso = langcodes.find(txt).language
            return langcodes.get(iso).language_name().capitalize()
        except Exception:
            return "English"

# ╭──────────────────────────────╮
# │ 7 •  PROMPT TEMPLATE         │
# ╰──────────────────────────────╯
PROMPT = (
    "You are a professional fact-checker.\n"
    "Write a concise (≤2 sentences) *correct* statement in the SAME language as "
    "the false claim. Do NOT negate the claim or mention that it was false; "
    "just state the correct fact. If one clear authoritative source is obvious "
    "(e.g., WHO, NASA, Eurostat), append it in brackets like “(WHO)”. "
    "If no single clear source, add nothing.\n\n"
    "False claim: «{claim}»\n"
    "Language: {lang}\n"
    "True statement:"
)

# ╭──────────────────────────────╮
# │ 8 •  CHAT WRAPPER            │
# ╰──────────────────────────────╯
def _chat(msgs):
    if LEGACY:
        r = openai.ChatCompletion.create(
                model=MODEL, messages=msgs, temperature=0, max_tokens=MAX_TOK)
        return r.choices[0].message.content.strip()
    r = openai.chat.completions.create(
            model=MODEL, messages=msgs, temperature=0, max_tokens=MAX_TOK)
    return r.choices[0].message.content.strip()

@backoff.on_exception(backoff.expo, (RateLimitError, APIError, Timeout),
                      max_time=300)
def make_true(claim, raw_lang):
    lang_name = normalise_lang(raw_lang)
    user_msg  = PROMPT.format(claim=claim, lang=lang_name)
    return _chat([{"role": "user", "content": user_msg}])

# ╭──────────────────────────────╮
# │ 9 •  MAIN LOOP               │
# ╰──────────────────────────────╯
with open(OUT_CSV, "a", newline="", encoding="utf-8") as fout:
    writer = csv.writer(fout)

    for i in range(done, len(records), BATCH_SZ):
        batch = records[i : i + BATCH_SZ]
        written = []
        for claim, raw_lang in batch:
            true_stmt = make_true(claim, raw_lang)

            cite = ""
            if true_stmt.endswith(")") and "(" in true_stmt:
                true_stmt, cite = true_stmt.rsplit("(", 1)
                cite = "(" + cite

            written.append((claim, true_stmt.strip(), cite.strip()))
        writer.writerows(written); fout.flush()

        print(f"✔ {i+len(batch):>6}/{len(records)} saved")
        time.sleep(SLEEP)

print("All pairs written →", OUT_CSV)
