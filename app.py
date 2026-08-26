# =============================================================================
# THE IRON SCHOLAR
# A training ledger and study companion.
# A seven-day programme with bioinformatics, immunology and machine learning
# between the sets. Records are held in a Supabase row when cloud storage is
# configured, and in a local data.json otherwise. Neither is version controlled.
#
# Run locally:   streamlit run app.py
# Deploy:        see README.md (Streamlit Community Cloud, free)
# =============================================================================

import json
import os
import random
import time
from datetime import date, datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

DATA_FILE = "data.json"
APP_NAME = "The Iron Scholar"
MOTTO = "Mens sana in corpore sano"

st.set_page_config(page_title=APP_NAME, layout="wide",
                   initial_sidebar_state="expanded")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="st-"], p, li, td, th, label {
    font-family: 'Source Serif 4', Georgia, 'Times New Roman', serif;
}
/* Streamlit draws its chevrons and other glyphs as Material Symbols
   ligatures. The selector above matches those spans too, and a serif face
   cannot resolve the ligature, so the raw icon name ("keyboard_arrow_right")
   prints on top of the label. Give the icon spans their font back. */
[data-testid="stIconMaterial"],
span[data-testid$="Icon"] {
    font-family: 'Material Symbols Rounded' !important;
}
h1, h2, h3 {
    font-family: 'EB Garamond', Georgia, serif;
    font-weight: 600;
    letter-spacing: 0.01em;
}
code, pre, .mono {
    font-family: 'IBM Plex Mono', Consolas, monospace;
}
.epigraph {
    font-family: 'EB Garamond', Georgia, serif;
    font-style: italic;
    font-size: 1.15rem;
    color: #201f1b;
    border-left: 2px solid #2f4b3f;
    padding: 0.2rem 0 0.2rem 1rem;
    margin: 0.4rem 0 0.6rem 0;
}
.epigraph-src {
    font-style: normal;
    font-variant: small-caps;
    letter-spacing: 0.06em;
    color: #6b675c;
    font-size: 0.9rem;
}
.bignum {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.6rem;
    color: #2f4b3f;
    line-height: 1.1;
}
.smallcap {
    font-variant: small-caps;
    letter-spacing: 0.08em;
    color: #6b675c;
}
.card-q {
    font-size: 1.15rem;
    font-weight: 600;
}
hr { border-top: 1px solid #d8d3c4; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def yt(query: str) -> str:
    """A YouTube search link that always works and surfaces current top tutorials."""
    return "https://www.youtube.com/results?search_query=" + query.replace(" ", "+")


def taipei_now() -> datetime:
    """Server clocks on Streamlit Cloud run UTC; Taipei is UTC+8, no DST."""
    return datetime.utcnow() + timedelta(hours=8)


def today_iso() -> str:
    return taipei_now().date().isoformat()


# -----------------------------------------------------------------------------
# Profile targets
# -----------------------------------------------------------------------------

TARGETS = {
    "calories": "2700 to 2900 kcal",
    "protein": "110 to 125 g",
    "fats": "70 to 80 g (favor unsaturated: nuts, fish, olive and canola oil)",
    "carbs": "380 to 420 g (rice, oats, sweet potato, fruit)",
    "water": "2.5 to 3 L",
    "sleep": "7 to 9 hours",
    "creatine": "5 g monohydrate, any time, every day",
    "gain rate": "0.25 to 0.5 kg per week (judge the weekly average)",
    "target weight": "65 to 68 kg (BMI 22.5 to 23.5)",
}

# -----------------------------------------------------------------------------
# Epigraphs (all ancient, public domain)
# -----------------------------------------------------------------------------

QUOTES = [
    ("No citizen has a right to be an amateur in the matter of physical training. "
     "What a disgrace it is for a man to grow old without ever seeing the beauty "
     "and strength of which his body is capable.", "Socrates, in Xenophon"),
    ("Mens sana in corpore sano. A sound mind in a sound body.", "Juvenal, Satire X"),
    ("We suffer more often in imagination than in reality.", "Seneca"),
    ("First say to yourself what you would be; and then do what you have to do.",
     "Epictetus"),
    ("The impediment to action advances action. What stands in the way becomes "
     "the way.", "Marcus Aurelius"),
    ("Excellence is never an accident. It is the result of intention, sincere "
     "effort, and intelligent execution.", "after Aristotle"),
    ("Difficulties strengthen the mind, as labor does the body.", "Seneca"),
]

# -----------------------------------------------------------------------------
# The seven-day plan (weekday index 0 = Monday)
# Exercise fields: name, zh, machine, sets, reps, start, rest (s), cue, link
# -----------------------------------------------------------------------------

PLAN = {
    0: {"title": "Push A", "focus": "Chest, shoulders, triceps", "type": "lift",
        "exercises": [
            {"name": "Machine Chest Press", "zh": "坐姿胸推機", "machine": "C zone (verify code)",
             "sets": 3, "reps": "8-12", "start": "15-20 kg", "rest": 90,
             "cue": "Handles at mid chest, shoulder blades pinned back, never slam the elbows locked.",
             "link": yt("chest press machine proper form beginner")},
            {"name": "Incline Dumbbell Press", "zh": "上斜啞鈴臥推", "machine": "Free weights, bench at 30 degrees",
             "sets": 3, "reps": "8-12", "start": "6-8 kg each", "rest": 90,
             "cue": "Bench one or two notches up (30 degrees), elbows about 45 degrees from the torso.",
             "link": yt("incline dumbbell press 30 degrees form")},
            {"name": "Seated Dumbbell Shoulder Press", "zh": "坐姿啞鈴肩推", "machine": "Free weights, bench upright",
             "sets": 3, "reps": "8-12", "start": "5-7.5 kg each", "rest": 90,
             "cue": "Start at ear height, forearms vertical, no hard arch in the lower back.",
             "link": yt("seated dumbbell shoulder press form beginner")},
            {"name": "Dumbbell Lateral Raise", "zh": "啞鈴側平舉", "machine": "Free weights",
             "sets": 3, "reps": "12-15", "start": "3-4 kg each", "rest": 60,
             "cue": "Slight fixed elbow bend, raise to shoulder height only, no swinging.",
             "link": yt("dumbbell lateral raise common mistakes")},
            {"name": "Cable Rope Triceps Pushdown", "zh": "繩索三頭下壓", "machine": "Cable station",
             "sets": 3, "reps": "10-15", "start": "15-20 kg", "rest": 60,
             "cue": "Elbows pinned to the ribs, split the rope at the bottom, squeeze one second.",
             "link": yt("rope tricep pushdown proper form")},
            {"name": "Overhead Cable Triceps Extension", "zh": "繩索過頭三頭伸展", "machine": "Cable station",
             "sets": 3, "reps": "10-15", "start": "10-15 kg", "rest": 60,
             "cue": "Face away from the stack, elbows point forward, feel the stretch behind the arm.",
             "link": yt("overhead cable tricep extension form")},
        ]},
    1: {"title": "Pull A", "focus": "Back, rear delts, biceps", "type": "lift",
        "exercises": [
            {"name": "Lat Pulldown", "zh": "滑輪下拉", "machine": "B zone (likely B2, verify)",
             "sets": 3, "reps": "8-12", "start": "25-32 kg", "rest": 90,
             "cue": "Lean back 10 to 15 degrees, pull the bar to the collarbone, elbows down and back.",
             "link": yt("lat pulldown proper form beginner")},
            {"name": "Seated Cable Row", "zh": "坐姿划船", "machine": "B zone or Low Row (verify)",
             "sets": 3, "reps": "8-12", "start": "25-30 kg", "rest": 90,
             "cue": "Pull to the belly button, squeeze the shoulder blades, full stretch forward.",
             "link": yt("seated cable row proper form")},
            {"name": "Assisted Pull-Up Machine", "zh": "輔助引體向上機", "machine": "Assisted station",
             "sets": 3, "reps": "6-10", "start": "assist 25-35 kg", "rest": 90,
             "cue": "Chin over the bar, three seconds down to a full hang. Reduce assist over time.",
             "link": yt("assisted pull up machine how to use")},
            {"name": "Cable Face Pull", "zh": "繩索面拉", "machine": "Cable station, rope at face height",
             "sets": 3, "reps": "12-15", "start": "10-15 kg", "rest": 60,
             "cue": "Pull toward the forehead, elbows high and wide, finish hands beside the ears.",
             "link": yt("cable face pull proper form")},
            {"name": "Dumbbell Biceps Curl", "zh": "啞鈴二頭彎舉", "machine": "Free weights",
             "sets": 3, "reps": "10-12", "start": "5-7.5 kg each", "rest": 60,
             "cue": "Elbows pinned at the sides, slow lowering, zero hip swing.",
             "link": yt("dumbbell bicep curl mistakes beginner")},
            {"name": "Back Extension", "zh": "羅馬椅背伸", "machine": "Roman chair",
             "sets": 3, "reps": "12-15", "start": "bodyweight", "rest": 60,
             "cue": "Hinge with a flat back, rise until the body is one straight line, no higher.",
             "link": yt("back extension roman chair proper form")},
        ]},
    2: {"title": "Legs A", "focus": "Quads, hamstrings, calves, core", "type": "lift",
        "exercises": [
            {"name": "Leg Press", "zh": "腿部推蹬機", "machine": "Leg zone",
             "sets": 3, "reps": "10-12", "start": "40-60 kg", "rest": 120,
             "cue": "Feet shoulder width, knees to 90 degrees, lower back flat on the pad, never lock out.",
             "link": yt("leg press machine proper form beginner")},
            {"name": "Leg Extension", "zh": "腿部伸展機", "machine": "Leg zone",
             "sets": 3, "reps": "12-15", "start": "20-30 kg", "rest": 75,
             "cue": "Knee joint at the machine pivot, full lockout, one second squeeze.",
             "link": yt("leg extension machine proper form")},
            {"name": "Seated Leg Curl", "zh": "坐姿腿彎舉", "machine": "Leg zone",
             "sets": 3, "reps": "12-15", "start": "15-25 kg", "rest": 75,
             "cue": "Curl the heels fully under the seat, resist the return.",
             "link": yt("seated leg curl proper form")},
            {"name": "Goblet Squat", "zh": "高腳杯深蹲", "machine": "Free weights",
             "sets": 3, "reps": "10-12", "start": "8-12 kg", "rest": 90,
             "cue": "Dumbbell at the chest, sit between the heels, chest tall, knees over toes.",
             "link": yt("goblet squat proper form beginner")},
            {"name": "Standing Calf Raise", "zh": "站姿提踵", "machine": "Calf machine or step",
             "sets": 3, "reps": "12-15", "start": "30-40 kg", "rest": 60,
             "cue": "Deep stretch at the bottom, one second pause at the top, no bouncing.",
             "link": yt("standing calf raise full range of motion")},
            {"name": "Plank + Cable Crunch", "zh": "平板支撐 + 跪姿繩索捲腹", "machine": "Mat + cable (Ab6 nearby)",
             "sets": 3, "reps": "30-45 s / 12-15", "start": "20-25 kg cable", "rest": 60,
             "cue": "Plank: straight line, glutes tight. Crunch: curl ribs toward pelvis, hips still.",
             "link": yt("kneeling cable crunch proper form")},
        ]},
    3: {"title": "Active Recovery", "focus": "Walk, core, mobility, sauna", "type": "recovery",
        "blocks": [
            "Incline treadmill walk, 20 to 25 min: 5 to 5.5 km/h at 6 to 10 percent incline. "
            "You should be able to speak full sentences. Do not run: running burns the surplus "
            "you are eating for, and the brisk incline walk is also the single best free tool "
            "you have for your lipid panel.",
            "Dead hangs from the pull-up bar, 3 x 20 to 30 s.",
            "Core circuit x 2 rounds: dead bug x 8 per side, bird dog x 8 per side, "
            "side plank 20 to 30 s per side.",
            "Full-body stretch, 30 s per side: hip flexor, hamstring, quad, chest doorway, "
            "lat hang, figure-4 glute, calf on a step.",
            "Optional: sauna or steam room, 8 to 10 min, then an extra 500 ml of water.",
        ]},
    4: {"title": "Push B", "focus": "Chest, shoulders, triceps, variations", "type": "lift",
        "exercises": [
            {"name": "Plate-Loaded Incline Chest Press", "zh": "上斜胸推(插片式)", "machine": "Plate-loaded incline press (code C5)",
             "sets": 3, "reps": "8-12", "start": "5-10 kg per side", "rest": 90,
             "cue": "Seat so handles meet the upper chest. Plate-loaded arms move independently: control both sides.",
             "link": yt("hammer strength incline press form")},
            {"name": "Flat Dumbbell Press", "zh": "平板啞鈴臥推", "machine": "Free weights",
             "sets": 3, "reps": "8-12", "start": "8-10 kg each", "rest": 90,
             "cue": "Shoulder blades pinched, elbows about 45 degrees, touch the outer chest.",
             "link": yt("flat dumbbell bench press proper form")},
            {"name": "Pec Deck", "zh": "蝴蝶機夾胸", "machine": "C zone (verify code)",
             "sets": 3, "reps": "12-15", "start": "20-30 kg", "rest": 75,
             "cue": "Handles at mid chest, slight fixed elbow bend, open only to a comfortable stretch.",
             "link": yt("pec deck machine proper form")},
            {"name": "Plate-Loaded Shoulder Press", "zh": "肩推(插片式)", "machine": "Plate-loaded shoulder press (code F11)",
             "sets": 3, "reps": "8-12", "start": "5-10 kg per side", "rest": 90,
             "cue": "Handles start at ear height, press without shrugging the ears up.",
             "link": yt("plate loaded shoulder press machine form")},
            {"name": "Cable Lateral Raise", "zh": "繩索側平舉", "machine": "Cable station, lowest setting",
             "sets": 3, "reps": "12-15", "start": "5-7.5 kg", "rest": 60,
             "cue": "Stand side-on, raise across the body to shoulder height, constant tension.",
             "link": yt("cable lateral raise proper form")},
            {"name": "Assisted Dips", "zh": "輔助雙槓下推", "machine": "Assisted station",
             "sets": 3, "reps": "8-12", "start": "assist 25-35 kg", "rest": 75,
             "cue": "Torso leaning slightly forward, elbows point back, upper arms to parallel.",
             "link": yt("assisted dip machine proper form")},
        ]},
    5: {"title": "Pull B", "focus": "Back, biceps, grip", "type": "lift",
        "exercises": [
            {"name": "Close-Grip Lat Pulldown", "zh": "窄距滑輪下拉", "machine": "B zone",
             "sets": 3, "reps": "8-12", "start": "25-32 kg", "rest": 90,
             "cue": "V handle, elbows drive to the ribs, big stretch at the top.",
             "link": yt("close grip lat pulldown form")},
            {"name": "One-Arm Dumbbell Row", "zh": "單臂啞鈴划船", "machine": "Free weights, flat bench",
             "sets": 3, "reps": "8-12 per side", "start": "10-12.5 kg", "rest": 75,
             "cue": "Back flat like a table, pull to the hip pocket, no torso twist.",
             "link": yt("one arm dumbbell row proper form")},
            {"name": "Reverse Pec Deck", "zh": "反向蝴蝶機", "machine": "C or S zone (verify)",
             "sets": 3, "reps": "12-15", "start": "15-25 kg", "rest": 60,
             "cue": "Face the pad, arms nearly straight, sweep back and squeeze the rear shoulders.",
             "link": yt("reverse pec deck rear delt form")},
            {"name": "EZ-Bar Curl", "zh": "EZ槓彎舉", "machine": "Free weights",
             "sets": 3, "reps": "10-12", "start": "10-15 kg total", "rest": 75,
             "cue": "The curved bar itself weighs about 7 kg. Elbows at the sides, slow lowering.",
             "link": yt("ez bar curl proper form")},
            {"name": "Hammer Curl", "zh": "錘式彎舉", "machine": "Free weights",
             "sets": 3, "reps": "10-12", "start": "5-7.5 kg each", "rest": 60,
             "cue": "Palms facing each other the whole rep. Forearms and brachialis.",
             "link": yt("hammer curl proper form")},
            {"name": "Farmer Carry", "zh": "農夫走路", "machine": "Free weights",
             "sets": 3, "reps": "30-40 m", "start": "12.5-16 kg each", "rest": 90,
             "cue": "Heaviest dumbbells you can hold with tall, perfect posture. Walk straight.",
             "link": yt("farmer carry proper form benefits")},
        ]},
    6: {"title": "Legs B", "focus": "Hinge, glutes, core. Deliberately lighter.", "type": "lift",
        "exercises": [
            {"name": "Smith Machine Squat", "zh": "史密斯深蹲", "machine": "Smith machine",
             "sets": 3, "reps": "10-12", "start": "empty bar to +5 kg per side", "rest": 120,
             "cue": "Feet slightly ahead of the bar line, bar on the upper traps, safeties set below your bottom.",
             "link": yt("smith machine squat beginner form")},
            {"name": "Dumbbell Romanian Deadlift", "zh": "啞鈴羅馬尼亞硬舉", "machine": "Free weights",
             "sets": 3, "reps": "10-12", "start": "10-12.5 kg each", "rest": 90,
             "cue": "Soft knees, push the hips back, flat back, dumbbells slide to mid-shin, squeeze glutes up.",
             "link": yt("dumbbell romanian deadlift proper form beginner")},
            {"name": "Walking Lunges", "zh": "走路弓步蹲", "machine": "Open floor",
             "sets": 3, "reps": "10 per leg", "start": "bodyweight to 8 kg", "rest": 75,
             "cue": "Long step, back knee kisses the floor, drive through the front heel.",
             "link": yt("walking lunges proper form")},
            {"name": "Hip Abduction Machine", "zh": "大腿外展機", "machine": "Leg zone",
             "sets": 2, "reps": "15", "start": "25-35 kg", "rest": 60,
             "cue": "Press the knees out, one second squeeze, slow return.",
             "link": yt("hip abduction machine proper form")},
            {"name": "Seated Calf Raise", "zh": "坐姿提踵", "machine": "Calf machine",
             "sets": 3, "reps": "15", "start": "20-30 kg", "rest": 60,
             "cue": "Deep stretch, pause at the top.",
             "link": yt("seated calf raise proper form")},
            {"name": "Hanging Knee Raise + Side Plank", "zh": "懸吊抬膝 + 側平板", "machine": "Pull-up bar / captain's chair",
             "sets": 3, "reps": "8-12 / 30 s per side", "start": "bodyweight", "rest": 60,
             "cue": "Curl the pelvis up as the knees rise, no swinging.",
             "link": yt("hanging knee raise proper form")},
        ]},
}

RULES = [
    "Tempo: two to three seconds down, one second up. Exhale on the effort.",
    "Effort: weeks 1 to 2 leave 3 to 4 reps in reserve. Week 3 onward, 1 to 2 in reserve.",
    "Progression: when you hit the top of the rep range on all sets with clean form, "
    "add 2.5 kg (or one pin, or one small plate per side) next session.",
    "If you cannot reach the bottom of the rep range, drop the weight about 10 percent.",
    "Log every set the moment you rack the weight.",
    "Every 7th or 8th week: deload. Same workouts, half the sets, about 70 percent weight.",
    "Sharp joint pain: stop that exercise. Soreness is fine; pain is information.",
    "Wrecked or slept under 6 hours: do the Active Recovery template instead. "
    "The calendar never breaks, only the intensity flexes.",
]

# -----------------------------------------------------------------------------
# Flashcards: tuned to a virologist / immunologist / bioinformatician
# -----------------------------------------------------------------------------

FLASHCARDS = {
    "Bioinformatics and Genomics": [
        ("FASTA vs FASTQ", "FASTA stores sequences alone; FASTQ adds a per-base quality string and is the standard raw output of sequencers."),
        ("What does Phred Q30 mean?", "A 1 in 1000 chance the base call is wrong, i.e. 99.9 percent accuracy. Q20 is 1 in 100."),
        ("What does BLAST actually do?", "Finds regions of local similarity between a query and a database using a fast heuristic approximation of Smith-Waterman."),
        ("Interpret an E-value", "The number of hits this good you would expect by chance given the database size. Lower is more significant; it is not a p-value."),
        ("Global vs local alignment", "Needleman-Wunsch aligns sequences end to end; Smith-Waterman finds the best-matching subregions."),
        ("SAM vs BAM vs CRAM", "SAM is the text format for read alignments; BAM is its compressed, indexable binary form; CRAM compresses further against the reference."),
        ("What lives in a VCF file?", "Variant calls: position, reference and alternate alleles, quality, filters and per-sample genotypes."),
        ("30x coverage means", "Each base is sequenced about 30 times on average. More depth gives more confident variant and consensus calls."),
        ("Define N50", "The contig length such that half the assembly is contained in contigs at least that long. A contiguity metric, not a quality guarantee."),
        ("Why hybrid assembly", "Long Nanopore reads span repeats to give structure; accurate Illumina reads polish the consensus. Best of both error profiles."),
        ("What is a k-mer?", "Any substring of length k. The unit of de Bruijn assemblers, genome sketching (Mash) and alignment-free comparison."),
        ("Burrows-Wheeler Transform in one line", "A reversible permutation of the text that clusters similar characters, enabling compressed full-text search. The engine of BWA and Bowtie."),
        ("Core vs accessory genome (pangenomics)", "Core genes are shared by all strains in the set; accessory genes vary between strains and often carry niche or virulence differences. The anvi'o view of your Chlamydia work."),
        ("16S rRNA sequencing tells you", "Which bacterial taxa are present and their relative abundance, via a conserved marker gene. It does not give functions; shotgun metagenomics does."),
        ("Raw counts vs TPM in RNA-seq", "Counts must be normalized before comparison. TPM normalizes for gene length then depth, comparable within a sample but shaky across experiments."),
        ("DESeq2 and edgeR model counts how?", "With a negative binomial distribution, sharing dispersion information across genes to find differential expression with few replicates."),
        ("What is an eQTL?", "A genetic variant associated with the expression level of a gene. GTEx catalogs them per tissue; they are the bridge in your TWAS pipeline."),
        ("TWAS in one sentence", "Impute genetically regulated expression from eQTL models into GWAS data, then test gene-level expression against the trait, prioritizing candidate causal genes."),
        ("Why control FDR in genomics?", "Testing 20000 genes guarantees false positives at p < 0.05. Benjamini-Hochberg controls the expected fraction of false discoveries instead."),
        ("Quasispecies", "The cloud of related viral variants within one host, generated by error-prone replication. Consensus genomes hide it; deep sequencing reveals it."),
        ("What does nf-core give you?", "Community-curated, versioned, containerized Nextflow pipelines: reproducibility, portability and CI-tested best practice for free."),
        ("Why trim reads before alignment?", "Adapters and low-quality tails create false mismatches and fragmented alignments, polluting variant calls and assemblies."),
    ],
    "Immunology and Virology": [
        ("Innate vs adaptive immunity", "Innate: fast, hardwired, pattern-based (macrophages, neutrophils, complement). Adaptive: slower, specific, with memory (T and B cells)."),
        ("MHC class I vs class II", "Class I presents intracellular peptides to CD8 T cells on nearly all cells; class II presents extracellular peptides to CD4 T cells on professional APCs."),
        ("Neutralizing vs binding antibodies", "Binding antibodies attach anywhere on the antigen; neutralizing antibodies block infection itself, usually by occluding the receptor-binding interface."),
        ("Antigenic drift vs shift", "Drift: gradual point mutations in surface proteins (seasonal flu). Shift: reassortment of genome segments creating novel subtypes (pandemic risk)."),
        ("What is R0?", "The average number of secondary infections from one case in a fully susceptible population. Herd immunity threshold is roughly 1 minus 1 over R0."),
        ("Ct value in qPCR", "The cycle at which fluorescence crosses threshold. Lower Ct means more starting template; each cycle is roughly a doubling."),
        ("The five antibody classes", "IgM first responder, IgG workhorse of memory, IgA mucosal, IgE allergy and parasites, IgD mostly a B cell receptor."),
        ("CD4 vs CD8 T cells", "CD4 helpers orchestrate responses via cytokines; CD8 cytotoxic cells kill infected cells presenting antigen on MHC I."),
        ("Viral tropism is set by", "Receptor availability, entry cofactors, and the intracellular environment a virus needs. Explains tissue-specific disease."),
        ("Cytokine storm", "A runaway positive-feedback release of inflammatory cytokines causing systemic damage, seen in severe influenza and COVID-19."),
        ("Why RNA viruses evolve fast", "RNA polymerases lack proofreading, so mutation rates are orders of magnitude higher than DNA replication, feeding quasispecies diversity."),
        ("Live attenuated vs inactivated vaccines", "Attenuated: replicating, strong broad immunity, cold-chain and safety constraints. Inactivated or subunit: safer, often needs adjuvant and boosters."),
        ("mRNA vaccine principle", "Deliver antigen-encoding mRNA in lipid nanoparticles; host cells translate the antigen, driving both antibody and T cell responses."),
        ("Original antigenic sin", "The immune system preferentially recalls responses to the first-encountered variant of a pathogen, sometimes at the cost of responses to new variants."),
    ],
    "Machine Learning and Statistics": [
        ("Overfitting in one line", "The model memorizes training noise and fails on new data. Detect with a held-out set; fight with more data, regularization, simpler models."),
        ("Bias-variance tradeoff", "Simple models underfit (high bias); flexible models swing with the sample (high variance). Tune complexity to minimize total error."),
        ("Train, validation, test", "Fit on train, tune hyperparameters on validation, report once on test. Touch test more than once and it becomes validation."),
        ("k-fold cross-validation", "Rotate which fold is held out so every point is validated once; average the score for a stabler estimate. Essential with small biological datasets."),
        ("L1 vs L2 regularization", "L1 (lasso) drives weights to exactly zero and selects features; L2 (ridge) shrinks all weights smoothly."),
        ("Gradient descent", "Step the weights downhill along the negative gradient of the loss. The learning rate sets the step size."),
        ("Learning rate too high vs too low", "Too high diverges or oscillates; too low crawls. It is usually the first hyperparameter worth tuning."),
        ("Precision vs recall", "Precision: of predicted positives, how many are right. Recall: of true positives, how many were found. Screening favors recall; confirmation favors precision."),
        ("ROC-AUC meaning", "The probability that a random positive scores higher than a random negative. 0.5 is a coin flip."),
        ("Why accuracy lies on imbalanced data", "Predicting everyone negative on a 99 to 1 dataset scores 99 percent. Use precision-recall curves, F1, or class-weighted losses."),
        ("Random forest", "Many decorrelated trees trained on bootstrapped samples and random feature subsets vote together. A very strong tabular baseline."),
        ("Gradient boosting", "Trees added sequentially, each fitting the errors of the ensemble so far. XGBoost and LightGBM dominate tabular competitions."),
        ("k-means in three steps", "Assign points to the nearest centroid, recompute centroids, repeat until stable. You must choose k and scale features first."),
        ("PCA in one line", "Rotate the data onto orthogonal axes of maximal variance; keep the top axes for compression and visualization. Standard first look at expression matrices."),
        ("Backpropagation", "The chain rule applied backward through the network to obtain the gradient of the loss for every weight."),
        ("Why nonlinear activations", "Without them, any stack of layers collapses to a single linear map. ReLU is the pragmatic default."),
        ("Dropout", "Randomly silence units during training so the network cannot rely on any single path. An ensemble-flavored regularizer."),
        ("Attention, in transformers", "Each token computes weighted views of all other tokens, learning what to look at. Parallelizable and long-range, unlike recurrence."),
        ("What is an embedding?", "A learned dense vector for a discrete item (word, gene, cell) placing similar items near each other."),
        ("Data leakage", "Information from evaluation sneaking into training, like scaling before splitting or duplicate patients across splits. Results look great, then collapse in deployment."),
    ],
}

# -----------------------------------------------------------------------------
# Machine directory seed: gym floor codes mapped to machine type.
# Confirm each one against the placard and rename it in the app.
# -----------------------------------------------------------------------------

MACHINE_SEED = [
    {"code": "C5",  "zone": "Chest",     "best_guess": "Plate-loaded chest press", "confirmed_name": "", "notes": "", "link": yt("hammer strength chest press how to")},
    {"code": "C6",  "zone": "Chest",     "best_guess": "Selectorised chest machine", "confirmed_name": "", "notes": "", "link": yt("chest press machine form")},
    {"code": "C10", "zone": "Chest",     "best_guess": "Chest press", "confirmed_name": "", "notes": "", "link": yt("chest press machine form")},
    {"code": "H15", "zone": "Chest area","best_guess": "Plate-loaded press, Hammer type", "confirmed_name": "", "notes": "", "link": yt("hammer strength machines guide")},
    {"code": "Ab6", "zone": "Abs",       "best_guess": "Abdominal crunch machine", "confirmed_name": "", "notes": "", "link": yt("ab crunch machine proper form")},
    {"code": "F11", "zone": "Functional, in front of gate", "best_guess": "Plate-loaded shoulder press or functional trainer", "confirmed_name": "", "notes": "", "link": yt("plate loaded shoulder press machine")},
    {"code": "S2",  "zone": "Shoulders", "best_guess": "Shoulder press machine", "confirmed_name": "", "notes": "", "link": yt("shoulder press machine form")},
    {"code": "S3",  "zone": "Shoulders", "best_guess": "Shoulder press machine, second unit", "confirmed_name": "", "notes": "", "link": yt("shoulder press machine form")},
    {"code": "S4",  "zone": "Shoulders", "best_guess": "Lighter shoulder machine, possibly lateral raise", "confirmed_name": "", "notes": "", "link": yt("lateral raise machine form")},
    {"code": "B2",  "zone": "Back",      "best_guess": "Lat pulldown or seated row", "confirmed_name": "", "notes": "", "link": yt("lat pulldown machine form")},
    {"code": "B5",  "zone": "Back",      "best_guess": "Back machine", "confirmed_name": "", "notes": "", "link": yt("seated row machine form")},
    {"code": "B8",  "zone": "Back",      "best_guess": "Light back or rear-delt station", "confirmed_name": "", "notes": "", "link": yt("rear delt machine form")},
    {"code": "LowRow", "zone": "Free weight area", "best_guess": "Plate-loaded low row", "confirmed_name": "", "notes": "", "link": yt("plate loaded low row form")},
]

# -----------------------------------------------------------------------------
# Resources: free, curated, no filler
# -----------------------------------------------------------------------------

RESOURCES = {
    "Training": [
        ("Hevy", "https://www.hevyapp.com", "Free workout logger with a demo video for every exercise. Mirror this app's plan there if you prefer logging on your phone."),
        ("MuscleWiki", "https://musclewiki.com", "Tap a muscle on a body map, get instant video demonstrations. Perfect mid-gym."),
        ("ExRx Exercise Directory", "https://exrx.net/Lists/Directory", "The classic academic reference for every exercise and its target muscles."),
        ("Jeff Nippard, YouTube", "https://www.youtube.com/@JeffNippard", "Science-based technique breakdowns. Watch the technique series for each new lift."),
        ("Renaissance Periodization, YouTube", "https://www.youtube.com/@RenaissancePeriodization", "Dr. Mike Israetel on how training volume and progression actually work."),
        ("Stronger by Science", "https://www.strongerbyscience.com", "Long-form evidence reviews when you want the primary-literature depth."),
    ],
    "Nutrition and Health": [
        ("MyFitnessPal", "https://www.myfitnesspal.com", "Calorie and protein tracking; good Taiwan convenience-store database."),
        ("Cronometer", "https://cronometer.com", "Stricter alternative with micronutrients, useful while watching lipids."),
        ("Examine", "https://examine.com", "Independent supplement evidence summaries. Read before buying anything beyond whey and creatine."),
        ("American Heart Association: cholesterol", "https://www.heart.org/en/health-topics/cholesterol", "Plain-language, guideline-based cholesterol information."),
    ],
    "Bioinformatics between sets": [
        ("Rosalind", "https://rosalind.info", "Bioinformatics problem solving as a puzzle ladder. One problem per rest day."),
        ("Biostars", "https://www.biostars.org", "The Q and A archive where every pipeline error you will ever hit has been hit before."),
        ("nf-core", "https://nf-co.re", "A curated collection of reproducible pipelines; the docs pages are excellent short reads."),
        ("EMBL-EBI Training", "https://www.ebi.ac.uk/training/on-demand", "Free short courses from the people who run the databases."),
        ("Galaxy Training Network", "https://training.galaxyproject.org", "Hands-on tutorials for nearly every omics workflow."),
        ("StatQuest, YouTube", "https://www.youtube.com/@statquest", "Josh Starmer. The best gentle-but-rigorous statistics and ML explainers in existence."),
        ("3Blue1Brown, YouTube", "https://www.youtube.com/@3blue1brown", "Visual linear algebra and neural networks. Ideal treadmill viewing."),
        ("Kaggle Learn", "https://www.kaggle.com/learn", "Free micro-courses: Python, pandas, intro ML, in-browser."),
        ("Hugging Face Learn", "https://huggingface.co/learn", "You are already on HF; their free NLP and deep learning courses are first rate."),
    ],
    "Form teachers, by specialty": [
        ("Scott Herman Fitness, YouTube", "https://www.youtube.com/results?search_query=scott+herman+fitness", "The encyclopedia of clear machine and dumbbell tutorials. Your first watch for nearly every movement in the plan."),
        ("Squat University, YouTube", "https://www.youtube.com/results?search_query=squat+university", "Dr. Aaron Horschig, physical therapist. The channel to open when something aches: knee, hip, shoulder, back."),
        ("Alan Thrall (Untamed Strength), YouTube", "https://www.youtube.com/results?search_query=alan+thrall+untamed+strength", "Plain-spoken barbell teaching. Your weeks 9 to 12 graduation path: squat, bench, deadlift, press, row."),
        ("StrengthLog exercise directory", "https://www.strengthlog.com/exercise-directory/", "Hundreds of exercises with free video demos and muscles-worked maps. The 30-second in-gym reference."),
    ],
    "The years ahead: free programs": [
        ("thefitness.wiki recommended routines", "https://thefitness.wiki/routines/", "The r/Fitness canon. Year 2 path: Basic Beginner Routine into GZCLP or 5/3/1 for Beginners, or the Reddit PPL."),
        ("Boostcamp", "https://www.boostcamp.app", "Free app carrying many of those same proven programs with built-in logging, for when you outgrow this plan."),
    ],
}

# -----------------------------------------------------------------------------
# Persistence
# -----------------------------------------------------------------------------

def default_data():
    return {
        # Deliberately empty. Biometrics belong in the data store, not in
        # source control. Set them once on the Data and Settings page.
        "profile": {"height_cm": None, "start_weight": None,
                    "target_weight": None},
        "weights": [],          # {date, kg}
        "workouts": [],         # {date, day, entries: {exercise: {w, r, s}}, note}
        "checklist": {},        # date -> {train, protein, creatine, sleep, calories}
        "machines": MACHINE_SEED,
        "lipids": [],           # {date, total, ldl, hdl, tg}
        "settings": {"gym_time": "17:30"},
    }


# Cloud backend: Supabase Postgres, one table, one row. See README.md for the
# table SQL and the secrets format. Nothing outside this block knows where the
# data lives; every page still reads st.session_state.data and calls save_data.

STORAGE_TABLE = "iron_scholar"
STORAGE_ROW = 1


def cloud_credentials():
    """Return (url, key) when both Supabase secrets are readable, else None.

    Any exception means local file mode. Reading st.secrets raises when there
    is no secrets.toml at all, which is the normal case for local development,
    so the app boots with zero setup.
    """
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        return None
    if not url or not key:
        return None
    return str(url), str(key)


@st.cache_resource(show_spinner=False)
def cloud_client():
    """The Supabase client, or None when cloud mode is not available."""
    creds = cloud_credentials()
    if creds is None:
        return None
    try:
        from supabase import create_client
        return create_client(creds[0], creds[1])
    except Exception as ex:
        st.session_state.storage_error = str(ex)
        return None


def storage_mode() -> str:
    """Which store the last load or save actually used: cloud or local."""
    return st.session_state.get("storage_mode", "local")


def merge_defaults(d: dict) -> dict:
    """Fold in any keys a newer version added, so old blobs survive."""
    base = default_data()
    for k, v in base.items():
        d.setdefault(k, v)
    return d


def read_local() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_data()
    return default_data()


def write_local(payload: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, ensure_ascii=False)


def load_data():
    client = cloud_client()
    if client is not None:
        try:
            res = (client.table(STORAGE_TABLE)
                   .select("data")
                   .eq("id", STORAGE_ROW)
                   .limit(1)
                   .execute())
            rows = res.data or []
            blob = rows[0].get("data") if rows else None
            st.session_state.storage_mode = "cloud"
            st.session_state.pop("storage_error", None)
            if isinstance(blob, dict) and blob:
                return merge_defaults(blob)
            return default_data()
        except Exception as ex:
            st.session_state.storage_error = str(ex)
    st.session_state.storage_mode = "local"
    return merge_defaults(read_local())


def save_data():
    payload = st.session_state.data
    client = cloud_client()
    if client is not None:
        try:
            client.table(STORAGE_TABLE).upsert({
                "id": STORAGE_ROW,
                "data": payload,
                "updated_at": taipei_now().isoformat() + "+08:00",
            }).execute()
            st.session_state.storage_mode = "cloud"
            st.session_state.pop("storage_error", None)
            return
        except Exception as ex:
            st.session_state.storage_error = str(ex)
            st.warning("Could not reach the cloud store, so this save went to "
                       "the local file instead. Nothing was lost. Reason: "
                       f"{ex}")
            st.session_state.storage_mode = "local"
    write_local(payload)


def passcode_gate():
    """Optional shared passcode. Absent secret means no gate at all.

    This is a curtain over a public URL, not real authentication.
    """
    try:
        expected = st.secrets["APP_PASSCODE"]
    except Exception:
        return
    if not expected:
        return
    if st.session_state.get("unlocked"):
        return
    st.title(APP_NAME)
    st.markdown(f"<span class='smallcap'>{MOTTO}</span>", unsafe_allow_html=True)
    given = st.text_input("Passcode", type="password")
    if given and given == str(expected):
        st.session_state.unlocked = True
        st.rerun()
    if given:
        st.error("That passcode is not correct.")
    else:
        st.caption("This app is private. Enter the passcode to continue.")
    st.stop()


passcode_gate()

if "data" not in st.session_state:
    st.session_state.data = load_data()

D = st.session_state.data

# -----------------------------------------------------------------------------
# Derived helpers
# -----------------------------------------------------------------------------

def latest_weight():
    """Most recent logged bodyweight, else the stated start weight, else None.

    Returns None until the user enters something; every caller must handle
    that, because the app ships with no biometrics of its own.
    """
    if D["weights"]:
        return D["weights"][-1]["kg"]
    return D["profile"].get("start_weight")


def done_dates() -> set:
    s = {w["date"] for w in D["workouts"]}
    s |= {d for d, c in D["checklist"].items() if c.get("train")}
    return s


def current_streak() -> int:
    dates = done_dates()
    day = taipei_now().date()
    streak = 0
    if day.isoformat() not in dates:
        day -= timedelta(days=1)   # streak survives until today is missed for good
    while day.isoformat() in dates:
        streak += 1
        day -= timedelta(days=1)
    return streak


def streak_figure() -> go.Figure:
    dates = done_dates()
    end = taipei_now().date()
    start = end - timedelta(days=7 * 20 - 1)
    start -= timedelta(days=start.weekday())
    n_weeks = ((end - start).days // 7) + 1
    z = [[None] * n_weeks for _ in range(7)]
    d = start
    while d <= end:
        col = (d - start).days // 7
        row = d.weekday()
        z[row][col] = 1 if d.isoformat() in dates else 0
        d += timedelta(days=1)
    fig = go.Figure(go.Heatmap(
        z=z, xgap=3, ygap=3, showscale=False,
        colorscale=[[0, "#e9e5d8"], [1, "#2f4b3f"]], zmin=0, zmax=1,
    ))
    fig.update_yaxes(tickvals=list(range(7)),
                     ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                     autorange="reversed", showgrid=False, fixedrange=True)
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_layout(height=190, margin=dict(l=10, r=10, t=10, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def last_logged(exercise: str):
    for w in reversed(D["workouts"]):
        e = w.get("entries", {}).get(exercise)
        if e:
            return e
    return None


def epigraph():
    q, src = QUOTES[taipei_now().timetuple().tm_yday % len(QUOTES)]
    st.markdown(
        f"<div class='epigraph'>{q}<br><span class='epigraph-src'>{src}</span></div>",
        unsafe_allow_html=True)


def meal_now() -> str:
    h = taipei_now().hour
    if 5 <= h < 9:
        return ("Breakfast window. Oats cooked in milk with a banana and nuts, plus two "
                "eggs. Oats and their soluble fiber are a direct LDL lever; start the day with them.")
    if 9 <= h < 11:
        return "Mid-morning. Unsweetened soy milk (無糖豆漿) and a handful of unsalted nuts."
    if 11 <= h < 14:
        return ("Lunch window. Bento with braised chicken leg (滷雞腿) or mackerel (鯖魚), extra rice "
                "(飯多), extra vegetables. Braised or steamed over deep-fried, today and most days.")
    if 14 <= h < 16:
        return "Afternoon. Roasted sweet potato (地瓜) from 7-Eleven and a tea egg or two."
    if 16 <= h < 18:
        return "Pre-workout. Onigiri (御飯糰) plus soy milk about 60 to 90 minutes before training."
    if 18 <= h < 21:
        return ("Post-workout and dinner. Whey shake with a banana right after training, then rice, "
                "a palm-plus portion of fish, chicken or tofu, and vegetables.")
    if 21 <= h < 23:
        return "Evening. A glass of milk or unsweetened yogurt if protein is short of target. Then wind down."
    return "Night. The most anabolic thing available right now is sleep. Seven hours minimum."


# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------

def page_today():
    now = taipei_now()
    plan = PLAN[now.weekday()]
    st.title(APP_NAME)
    st.markdown(f"<span class='smallcap'>{MOTTO} &nbsp;|&nbsp; "
                f"{now.strftime('%A, %d %B %Y')} &nbsp;|&nbsp; Taipei</span>",
                unsafe_allow_html=True)
    epigraph()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<span class='smallcap'>Current streak</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='bignum'>{current_streak()} d</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<span class='smallcap'>Today's session</span>", unsafe_allow_html=True)
        st.markdown(f"### {plan['title']}")
        st.caption(plan["focus"])
    with c3:
        w = latest_weight()
        tw = D["profile"].get("target_weight")
        st.markdown("<span class='smallcap'>Bodyweight</span>", unsafe_allow_html=True)
        if w is None:
            st.markdown("<div class='bignum'>&mdash;</div>", unsafe_allow_html=True)
            st.caption("Log one below; it is stored only on this machine.")
        else:
            st.markdown(f"<div class='bignum'>{w:.1f} kg</div>", unsafe_allow_html=True)
            st.caption(f"Target {tw:.0f} kg" if tw
                       else "Set a target in Data and Settings.")

    st.divider()
    st.subheader("Right now")
    st.write(meal_now())

    st.divider()
    st.subheader("Daily ledger")
    st.caption("Tick as the day passes. The training tick keeps the streak alive; "
               "on Thursdays the recovery session counts in full.")
    today = today_iso()
    cl = D["checklist"].get(today, {})
    cols = st.columns(5)
    labels = [("train", "Trained"), ("calories", "Calories 2700+"),
              ("protein", "Protein 110 g+"), ("creatine", "Creatine 5 g"),
              ("sleep", "Slept 7 h+")]
    new_cl = {}
    for col, (key, label) in zip(cols, labels):
        with col:
            new_cl[key] = st.checkbox(label, value=bool(cl.get(key)), key=f"cl_{key}")
    if new_cl != cl:
        D["checklist"][today] = new_cl
        save_data()

    st.divider()
    st.subheader("Log bodyweight")
    st.caption("Every morning, after the bathroom, before food. Judge only the weekly average.")
    wcol1, wcol2 = st.columns([1, 3])
    with wcol1:
        wt = st.number_input("kg", min_value=40.0, max_value=120.0, step=0.1,
                             value=float(w) if w is not None else None,
                             placeholder="kg", label_visibility="collapsed")
    with wcol2:
        if st.button("Save today's weight", disabled=wt is None):
            D["weights"] = [x for x in D["weights"] if x["date"] != today]
            D["weights"].append({"date": today, "kg": round(wt, 1)})
            D["weights"].sort(key=lambda x: x["date"])
            save_data()
            st.success("Weight recorded.")


def page_plan():
    st.title("The Seven Days")
    st.caption("Push, Pull, Legs, Recover, Push, Pull, Legs. Every muscle twice a week, "
               "every session inside 40 to 60 minutes, no day off and no day wasted.")
    for i in range(7):
        plan = PLAN[i]
        day_name = ["Monday", "Tuesday", "Wednesday", "Thursday",
                    "Friday", "Saturday", "Sunday"][i]
        with st.expander(f"{day_name}: {plan['title']}. {plan['focus']}",
                         expanded=(i == taipei_now().weekday())):
            if plan["type"] == "recovery":
                for b in plan["blocks"]:
                    st.write("- " + b)
            else:
                rows = []
                for e in plan["exercises"]:
                    rows.append({
                        "Exercise": f"{e['name']} ({e['zh']})",
                        "Where": e["machine"],
                        "Sets x Reps": f"{e['sets']} x {e['reps']}",
                        "Start": e["start"],
                        "Rest": f"{e['rest']} s",
                        "Cue": e["cue"],
                        "Tutorial": e["link"],
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                             column_config={"Tutorial": st.column_config.LinkColumn(
                                 "Tutorial", display_text="watch")})
    st.divider()
    st.subheader("Standing rules")
    for r in RULES:
        st.write("- " + r)


def page_log():
    st.title("Log a Session")
    day_names = ["Monday Push A", "Tuesday Pull A", "Wednesday Legs A",
                 "Thursday Recovery", "Friday Push B", "Saturday Pull B",
                 "Sunday Legs B"]
    idx = st.selectbox("Session", range(7), index=taipei_now().weekday(),
                       format_func=lambda i: day_names[i])
    plan = PLAN[idx]

    if plan["type"] == "recovery":
        st.write("Recovery day. Walk, hang, stretch, breathe, sauna.")
        for b in plan["blocks"]:
            st.write("- " + b)
        if st.button("Mark recovery complete"):
            today = today_iso()
            D["workouts"].append({"date": today, "day": plan["title"], "entries": {}})
            D["checklist"].setdefault(today, {})["train"] = True
            save_data()
            st.success("Recovery logged. The streak holds.")
        return

    st.caption("Enter your top working weight and the reps of your best set. "
               "Fields prefill from your last session so the double-progression "
               "decision is staring at you: same weight, or plus 2.5 kg.")
    entries = {}
    for e in plan["exercises"]:
        prev = last_logged(e["name"])
        with st.expander(f"{e['name']} ({e['zh']})  |  target {e['sets']} x {e['reps']}",
                         expanded=False):
            st.caption(f"{e['cue']}  [Tutorial]({e['link']})")
            if prev:
                st.caption(f"Last time: {prev['w']} kg x {prev['r']} reps x {prev['s']} sets")
            c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
            with c1:
                wv = st.number_input("Weight kg", 0.0, 500.0,
                                     float(prev["w"]) if prev else 0.0, 2.5,
                                     key=f"w_{idx}_{e['name']}")
            with c2:
                rv = st.number_input("Best-set reps", 0, 50,
                                     int(prev["r"]) if prev else 0, 1,
                                     key=f"r_{idx}_{e['name']}")
            with c3:
                sv = st.number_input("Sets done", 0, 10,
                                     int(prev["s"]) if prev else e["sets"], 1,
                                     key=f"s_{idx}_{e['name']}")
            with c4:
                done = st.checkbox("Include", value=False, key=f"d_{idx}_{e['name']}")
            if done:
                entries[e["name"]] = {"w": wv, "r": rv, "s": sv}

    note = st.text_input("Session note (optional): energy, pain, machine codes discovered")
    if st.button("Save session"):
        if not entries:
            st.warning("Tick 'Include' on at least one exercise before saving.")
        else:
            today = today_iso()
            D["workouts"].append({"date": today, "day": plan["title"],
                                  "entries": entries, "note": note})
            D["checklist"].setdefault(today, {})["train"] = True
            save_data()
            st.success(f"Session saved: {len(entries)} exercises. The streak holds.")


def page_rest():
    st.title("Rest Timer and Study")
    st.caption("Ninety seconds of rest is ninety seconds of tuition. Pick your decks, "
               "start the timer, and read while the muscle recovers. One card per rest, "
               "roughly eighteen cards per session, over a hundred per week.")

    decks = st.multiselect("Decks", list(FLASHCARDS.keys()),
                           default=list(FLASHCARDS.keys()))
    dur = st.select_slider("Rest length (seconds)", options=[60, 75, 90, 120], value=90)

    pool = [c for d in decks for c in FLASHCARDS[d]]
    if not pool:
        st.info("Select at least one deck.")
        return

    if st.button("Start rest and draw a card", type="primary"):
        q, a = random.choice(pool)
        st.markdown(f"<div class='card-q'>{q}</div>", unsafe_allow_html=True)
        st.write(a)
        st.divider()
        bar = st.progress(0.0)
        slot = st.empty()
        for i in range(dur, 0, -1):
            slot.markdown(f"<div class='bignum'>{i}</div>", unsafe_allow_html=True)
            bar.progress((dur - i + 1) / dur)
            time.sleep(1)
        slot.markdown("<div class='bignum'>Lift.</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("Study mode, outside the gym")
    if "study_card" not in st.session_state:
        st.session_state.study_card = random.choice(pool)
    if st.button("Next card"):
        st.session_state.study_card = random.choice(pool)
    q, a = st.session_state.study_card
    st.markdown(f"<div class='card-q'>{q}</div>", unsafe_allow_html=True)
    with st.expander("Reveal answer"):
        st.write(a)
    st.caption(f"{len(pool)} cards loaded across {len(decks)} deck(s).")


def page_progress():
    st.title("Progress")

    st.subheader("The consistency ledger")
    st.caption("Twenty weeks. Fill it the way you fill a contribution graph.")
    st.plotly_chart(streak_figure(), use_container_width=True,
                    config={"displayModeBar": False})

    st.subheader("Bodyweight")
    if D["weights"]:
        dfw = pd.DataFrame(D["weights"])
        dfw["date"] = pd.to_datetime(dfw["date"])
        dfw["7-day mean"] = dfw["kg"].rolling(7, min_periods=1).mean()
        fig = go.Figure()
        fig.add_scatter(x=dfw["date"], y=dfw["kg"], mode="markers",
                        name="daily", marker=dict(color="#8f6f3a", size=6))
        fig.add_scatter(x=dfw["date"], y=dfw["7-day mean"], mode="lines",
                        name="7-day mean", line=dict(color="#2f4b3f", width=3))
        tw = D["profile"].get("target_weight")
        if tw:
            fig.add_hline(y=tw, line_dash="dot", line_color="#6b675c",
                          annotation_text=f"target {tw:.0f} kg")
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)
        wk = dfw["kg"].tail(7).mean()
        st.caption(f"Seven-day average: {wk:.1f} kg. If this number is flat for two "
                   "weeks, add 200 kcal per day.")
    else:
        st.info("Log a bodyweight on the Today page and the chart appears here.")

    st.subheader("Lifts")
    names = sorted({n for w in D["workouts"] for n in w.get("entries", {})})
    if names:
        pick = st.selectbox("Exercise", names)
        rows = [{"date": w["date"], "kg": w["entries"][pick]["w"],
                 "reps": w["entries"][pick]["r"]}
                for w in D["workouts"] if pick in w.get("entries", {})]
        dfe = pd.DataFrame(rows)
        dfe["date"] = pd.to_datetime(dfe["date"])
        fig2 = go.Figure()
        fig2.add_scatter(x=dfe["date"], y=dfe["kg"], mode="lines+markers",
                         line=dict(color="#2f4b3f", width=3),
                         marker=dict(size=7, color="#8f6f3a"))
        fig2.update_layout(height=300, margin=dict(l=10, r=10, t=20, b=10),
                           paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="top working weight, kg")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Log a session and every exercise becomes a chart here.")


def page_nutrition():
    st.title("Nutrition, Localized")
    st.caption("Taiwan. Convenience stores, bento shops and lipid numbers taken "
               "seriously without abandoning the surplus.")

    st.subheader("Daily targets")
    st.dataframe(pd.DataFrame([{"Target": k, "Value": v} for k, v in TARGETS.items()]),
                 hide_index=True, use_container_width=True)

    st.subheader("Right now")
    st.write(meal_now())

    st.subheader("A model day, about 2800 kcal, heart-aware")
    day = [
        ("07:30", "Oats cooked in low-fat milk, banana, walnuts, plus 2 eggs",
         "Oat beta-glucan actively lowers LDL. Two yolks, not three, while the panel is unverified; add whites freely."),
        ("12:30", "Bento: braised chicken leg 滷雞腿 or grilled mackerel 鯖魚, extra rice 飯多, double vegetables",
         "Mackerel and saba bento are cheap omega-3. Braised and steamed beat deep-fried every single time."),
        ("15:30", "Roasted sweet potato 地瓜 + tea egg 茶葉蛋 + unsweetened soy milk 無糖豆漿",
         "Soy protein has a small LDL-lowering effect of its own. The 7-Eleven bulking stack."),
        ("16:45", "Onigiri 御飯糰 before the gym", "Fast carbs, low fat, trains well."),
        ("19:00", "Whey + banana immediately after training", "Cheapest protein per NT dollar you will find."),
        ("20:00", "Rice + palm-plus of fish, chicken breast 舒肥雞胸, or tofu + vegetables",
         "Family Mart and 7-Eleven sous-vide chicken breast: 25 g protein, almost no saturated fat."),
        ("21:30", "Milk or unsweetened yogurt if protein is short", "Slow protein before sleep."),
    ]
    for t, food, why in day:
        st.markdown(f"**{t}**  {food}")
        st.caption(why)

    st.subheader("Swap table: same calories, kinder lipids")
    swaps = pd.DataFrame([
        {"Instead of": "Fried chicken cutlet 炸雞排", "Choose": "Braised chicken leg 滷雞腿", "Why": "Deep-fry oil and batter are the main saturated and trans fat load in a Taiwan street diet."},
        {"Instead of": "鹽酥雞 popcorn chicken night", "Choose": "滷味 braised egg, tofu, kelp plate", "Why": "Same night-market ritual, fraction of the oxidized oil."},
        {"Instead of": "Instant noodles as a staple", "Choose": "Rice, sweet potato, oats", "Why": "Palm-oil fried noodle blocks are quiet saturated fat."},
        {"Instead of": "Pastries and pineapple cake daily", "Choose": "Fruit, nuts, dark chocolate square", "Why": "Bakery shortening is a lipid tax on breakfast."},
        {"Instead of": "Whole-fat milk three times a day", "Choose": "Low-fat milk plus nuts", "Why": "Keeps the calories, shifts fat from saturated to unsaturated."},
        {"Instead of": "Mass gainer powder", "Choose": "Whey plus real rice and bananas", "Why": "Gainers are expensive sugar; your kitchen is cheaper and cleaner."},
    ])
    st.dataframe(swaps, hide_index=True, use_container_width=True)

    st.subheader("Supplements: the honest list")
    st.write("Whey protein, one to two scoops a day, purely to reach 110 g protein cheaply. "
             "Creatine monohydrate, 5 g every day, the most studied supplement in existence, "
             "with extra water. Everything else on the shelf is marketing until proven otherwise "
             "on Examine. If you have any kidney condition, clear creatine with a doctor first.")


def page_health():
    st.title("Cholesterol and Health")
    st.caption("Borderline numbers at 25, caught early, respond extremely well to exactly "
               "what you are already doing: daily training, fish, fiber, sleep. Track the "
               "panel here and watch it move.")

    st.subheader("Record a lipid panel")
    with st.form("lipid_form"):
        c0, c1, c2, c3, c4 = st.columns(5)
        with c0:
            ldate = st.date_input("Date", value=taipei_now().date())
        with c1:
            total = st.number_input("Total (mg/dL)", 0, 500, 0)
        with c2:
            ldl = st.number_input("LDL (mg/dL)", 0, 400, 0)
        with c3:
            hdl = st.number_input("HDL (mg/dL)", 0, 150, 0)
        with c4:
            tg = st.number_input("Triglycerides (mg/dL)", 0, 1000, 0)
        if st.form_submit_button("Save panel"):
            D["lipids"].append({"date": ldate.isoformat(), "total": total,
                                "ldl": ldl, "hdl": hdl, "tg": tg})
            D["lipids"].sort(key=lambda x: x["date"])
            save_data()
            st.success("Panel saved.")
    st.caption("If your Taiwanese lab reports mmol/L: cholesterol values x 38.67, "
               "triglycerides x 88.57 to convert to mg/dL.")

    if D["lipids"]:
        dfl = pd.DataFrame(D["lipids"])
        dfl["date"] = pd.to_datetime(dfl["date"])
        fig = go.Figure()
        for col, colr in [("total", "#20201b"), ("ldl", "#7a3b2e"),
                          ("hdl", "#2f4b3f"), ("tg", "#8f6f3a")]:
            fig.add_scatter(x=dfl["date"], y=dfl[col], mode="lines+markers",
                            name=col.upper(), line=dict(color=colr, width=2))
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          legend=dict(orientation="h"), yaxis_title="mg/dL")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Reference ranges (ATP III, mg/dL)")
    ref = pd.DataFrame([
        {"Marker": "Total cholesterol", "Desirable": "< 200", "Borderline": "200 to 239", "High": ">= 240"},
        {"Marker": "LDL", "Desirable": "< 100 optimal, < 130 near-optimal", "Borderline": "130 to 159", "High": ">= 160"},
        {"Marker": "HDL", "Desirable": ">= 60 protective", "Borderline": "40 to 59", "High": "< 40 is the risk direction"},
        {"Marker": "Triglycerides", "Desirable": "< 150", "Borderline": "150 to 199", "High": ">= 200"},
    ])
    st.dataframe(ref, hide_index=True, use_container_width=True)

    st.subheader("The levers, ranked by evidence")
    for line in [
        "Aerobic minutes: your Thursday incline walks and daily training raise HDL and cut "
        "triglycerides. This is the strongest card you hold and you are already playing it.",
        "Soluble fiber: oats every morning, beans and vegetables daily. Beta-glucan binds "
        "cholesterol in the gut.",
        "Fat quality over fat quantity: keep total fat for the bulk, but shift it from fried "
        "and pastry fat toward fish, nuts, olive and canola oil.",
        "Fatty fish twice a week: mackerel and saba bento make this trivially easy in Taiwan.",
        "Eggs: current evidence says saturated fat matters far more than dietary cholesterol, "
        "but with an unverified borderline panel, two yolks a day plus extra whites is the "
        "sensible middle path. Revisit once you have real numbers trending well.",
        "Sleep 7 to 9 hours: short sleep independently worsens lipid profiles.",
        "Recheck the panel after 10 to 12 weeks of this routine and log it above.",
    ]:
        st.write("- " + line)

    st.info("This page is educational tracking, not medical advice. Get an actual panel "
            "from a clinic to establish your baseline, and discuss the results with a "
            "physician, especially before any supplement beyond whey and creatine.")


def page_machines():
    st.title("Machine Directory")
    st.caption("Every code from your own training notes, pre-seeded with my best guess. "
               "Your ten-minute field mission: photograph the placard on each machine, "
               "then type its real name into the Confirmed name column. After that this "
               "page is the manual for your exact gym floor.")
    st.markdown("Ask staff: 不好意思，請問這台機器的名稱是什麼？ "
                "(Excuse me, what is this machine called?)")

    df = pd.DataFrame(D["machines"])
    edited = st.data_editor(
        df, num_rows="dynamic", use_container_width=True, hide_index=True,
        column_config={
            "code": st.column_config.TextColumn("Code", width="small"),
            "zone": st.column_config.TextColumn("Zone"),
            "best_guess": st.column_config.TextColumn("Best guess"),
            "confirmed_name": st.column_config.TextColumn("Confirmed name (from placard)"),
            "notes": st.column_config.TextColumn("Seat settings and notes"),
            "link": st.column_config.LinkColumn("Tutorial", display_text="watch"),
        })
    if st.button("Save directory"):
        D["machines"] = edited.fillna("").to_dict("records")
        save_data()
        st.success("Directory saved.")

    st.subheader("Reading your gym's labels")
    for line in [
        "Letter = zone: C chest, S shoulders, B back, Ab abdominals, F functional or "
        "free-standing zone. Legs will carry their own letter; add codes as you find them.",
        "One number, like B2 (42.5 kg): a pin-stack machine, the number is the stack setting.",
        "Two numbers, like C5 (10+10): plate-loaded, you load discs on each side. Log per-side weight.",
        "0 kg on a plate-loaded machine still moves the empty arms: that resistance is real, "
        "just unrecorded. Note the machine and progress by adding discs.",
    ]:
        st.write("- " + line)


def page_reminders():
    st.title("Reminders")
    st.caption("A web app cannot ring your phone, so we do it properly: generate a calendar "
               "file once, import it, and your phone reminds you every single day forever, "
               "online or offline.")

    t = st.time_input("Daily gym time",
                      value=datetime.strptime(D["settings"].get("gym_time", "17:30"),
                                              "%H:%M").time())
    add_creatine = st.checkbox("Add a daily creatine reminder at 09:00", value=True)
    add_sleep = st.checkbox("Add a wind-down reminder at 22:30", value=True)

    if st.button("Generate calendar file"):
        D["settings"]["gym_time"] = t.strftime("%H:%M")
        save_data()
        start = taipei_now().date().strftime("%Y%m%d")
        def vevent(uid, hhmm, summary, desc):
            return ("BEGIN:VEVENT\r\nUID:" + uid + "@ironscholar\r\n"
                    "DTSTART:" + start + "T" + hhmm + "00\r\n"
                    "RRULE:FREQ=DAILY\r\nSUMMARY:" + summary + "\r\n"
                    "DESCRIPTION:" + desc + "\r\n"
                    "BEGIN:VALARM\r\nTRIGGER:-PT30M\r\nACTION:DISPLAY\r\n"
                    "DESCRIPTION:" + summary + "\r\nEND:VALARM\r\nEND:VEVENT\r\n")
        ics = ("BEGIN:VCALENDAR\r\nVERSION:2.0\r\n"
               "PRODID:-//The Iron Scholar//EN\r\n")
        ics += vevent("gym", t.strftime("%H%M"), "Gym: The Iron Scholar",
                      "Todays session is on the Today page. The streak holds.")
        if add_creatine:
            ics += vevent("creatine", "0900", "Creatine 5 g", "Any liquid, every day.")
        if add_sleep:
            ics += vevent("sleep", "2230", "Wind down",
                          "Muscle is built in bed. Screens off soon.")
        ics += "END:VCALENDAR\r\n"
        st.download_button("Download iron_scholar_reminders.ics", ics,
                           file_name="iron_scholar_reminders.ics",
                           mime="text/calendar")
        st.success("File ready below. Import once; it repeats daily on its own.")

    st.subheader("How to import")
    for line in [
        "Google Calendar (Android and web): calendar.google.com, gear icon, Settings, "
        "Import and export, select the file, Import.",
        "iPhone: open the downloaded file and tap Add All to Calendar.",
        "Bonus: open this app in your phone browser, share menu, Add to Home Screen. "
        "It then launches full-screen like a native app.",
    ]:
        st.write("- " + line)


def page_resources():
    st.title("The Library")
    st.caption("Free, curated, and only things worth your attention. Everything else was cut.")
    for cat, items in RESOURCES.items():
        st.subheader(cat)
        for name, url, why in items:
            st.markdown(f"[{name}]({url})")
            st.caption(why)


def page_data():
    st.title("Data and Settings")

    st.subheader("Profile")
    st.caption("Blank until you fill it in. These values are written only to the "
               "local data.json, which is excluded from version control.")

    def _opt(v):
        return float(v) if v is not None else None

    p = D["profile"]
    c1, c2, c3 = st.columns(3)
    with c1:
        h = st.number_input("Height cm", 100.0, 230.0, _opt(p.get("height_cm")),
                            0.1, placeholder="cm")
    with c2:
        sw = st.number_input("Start weight kg", 30.0, 150.0,
                             _opt(p.get("start_weight")), 0.1, placeholder="kg")
    with c3:
        tw = st.number_input("Target weight kg", 30.0, 150.0,
                             _opt(p.get("target_weight")), 0.5, placeholder="kg")
    if st.button("Save profile"):
        p.update({"height_cm": h, "start_weight": sw, "target_weight": tw})
        save_data()
        st.success("Profile saved.")

    cur = D["weights"][-1]["kg"] if D["weights"] else sw
    if cur and h:
        bmi = cur / ((h / 100) ** 2)
        st.caption(f"Current BMI: {bmi:.1f}. Normal range 18.5 to 24.9.")
    else:
        st.caption("Enter a height and a weight for a BMI reading.")

    st.subheader("Storage")
    err = st.session_state.get("storage_error")
    if storage_mode() == "cloud":
        st.success("Cloud connected. Every change is saved to Supabase and "
                   "survives restarts, redeploys and sleep.")
    else:
        st.info("Local file mode. Everything is written to data.json beside "
                "app.py, on this machine only.")
        if err:
            st.warning("Cloud storage is configured but could not be reached, "
                       f"so the local file is in use. Reason: {err}")
        elif cloud_credentials() is None:
            st.caption("Add SUPABASE_URL and SUPABASE_KEY to the secrets to "
                       "turn on cloud storage. See README.md.")

    st.subheader("Backup and restore")
    if storage_mode() == "cloud":
        st.caption("Cloud mode keeps your data safe on its own. A backup is "
                   "still worth taking before any large change.")
    else:
        st.caption("Important: on Streamlit Community Cloud the disk resets "
                   "whenever the app restarts or redeploys. In local file mode, "
                   "download a backup after every few sessions; restoring takes "
                   "one upload. Running the app on your own machine keeps the "
                   "file permanently.")
    st.download_button("Download backup (JSON)",
                       json.dumps(D, indent=1, ensure_ascii=False),
                       file_name=f"iron_scholar_backup_{today_iso()}.json",
                       mime="application/json")
    up = st.file_uploader("Restore from backup", type=["json"])
    st.caption("Restore is also the migration path: upload an old data.json "
               "here once and it becomes the contents of the active store.")
    if up is not None and st.button("Restore now"):
        try:
            st.session_state.data = merge_defaults(json.load(up))
            save_data()
            st.success("Backup restored.")
            st.rerun()
        except Exception as ex:
            st.error(f"Could not read that file: {ex}")


# -----------------------------------------------------------------------------
# Router
# -----------------------------------------------------------------------------

PAGES = {
    "Today": page_today,
    "The Seven Days": page_plan,
    "Log a Session": page_log,
    "Rest Timer and Study": page_rest,
    "Progress": page_progress,
    "Nutrition": page_nutrition,
    "Cholesterol and Health": page_health,
    "Machine Directory": page_machines,
    "Reminders": page_reminders,
    "The Library": page_resources,
    "Data and Settings": page_data,
}

with st.sidebar:
    st.markdown(f"## {APP_NAME}")
    st.markdown(f"<span class='smallcap'>{MOTTO}</span>", unsafe_allow_html=True)
    st.divider()
    choice = st.radio("Sections", list(PAGES.keys()), label_visibility="collapsed")
    st.divider()
    st.markdown(f"<span class='smallcap'>Streak</span> "
                f"<span class='mono'>{current_streak()} days</span>",
                unsafe_allow_html=True)
    st.caption(MOTTO + ".")

PAGES[choice]()
