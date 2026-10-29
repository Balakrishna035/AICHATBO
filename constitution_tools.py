"""
constitution_tools.py - Specialized Knowledge Base and Tools for Constitutional Law.

In Agentic AI:
The agent uses these tools as its factual reference library.
Instead of guessing or hallucinating legal provisions, the agent calls these
functions to retrieve exact constitutional texts, writs, rights, and amendments.
"""

from typing import Dict, Any, Optional

# --- 1. PREAMBLE ---
PREAMBLE_TEXT = (
    "WE, THE PEOPLE OF INDIA, having solemnly resolved to constitute India into a "
    "SOVEREIGN SOCIALIST SECULAR DEMOCRATIC REPUBLIC and to secure to all its citizens:\n\n"
    "• JUSTICE, social, economic and political;\n"
    "• LIBERTY of thought, expression, belief, faith and worship;\n"
    "• EQUALITY of status and of opportunity; and to promote among them all\n"
    "• FRATERNITY assuring the dignity of the individual and the unity and integrity of the Nation;\n\n"
    "IN OUR CONSTITUENT ASSEMBLY this twenty-sixth day of November, 1949, do HEREBY "
    "ADOPT, ENACT AND GIVE TO OURSELVES THIS CONSTITUTION."
)

# --- 2. KEY CONSTITUTIONAL ARTICLES ---
ARTICLES_DB = {
    "1": {
        "title": "Name and territory of the Union",
        "part": "Part I: The Union and its Territory",
        "summary": "India, that is Bharat, shall be a Union of States rather than a federation of states.",
        "significance": "Defines the territorial boundary and political identity of India."
    },
    "14": {
        "title": "Equality before Law",
        "part": "Part III: Fundamental Rights",
        "summary": "The State shall not deny to any person equality before the law or the equal protection of the laws within India.",
        "significance": "Bars discrimination and ensures rule of law for citizens and non-citizens alike."
    },
    "15": {
        "title": "Prohibition of discrimination",
        "part": "Part III: Fundamental Rights",
        "summary": "Prohibits discrimination on grounds only of religion, race, caste, sex, or place of birth.",
        "significance": "Allows special provisions for women, children, and socially/educationally backward classes."
    },
    "19": {
        "title": "Protection of Six Freedoms",
        "part": "Part III: Fundamental Rights",
        "summary": "Guarantees 6 democratic freedoms: (a) speech and expression, (b) peaceful assembly, (c) forming associations/unions, (d) free movement throughout India, (e) residing and settling anywhere in India, and (g) practicing any profession or trade.",
        "significance": "The backbone of civil liberties in India, subject to reasonable restrictions (public order, security)."
    },
    "21": {
        "title": "Protection of Life and Personal Liberty",
        "part": "Part III: Fundamental Rights",
        "summary": "No person shall be deprived of his life or personal liberty except according to procedure established by law.",
        "significance": "The most widely interpreted article by Supreme Court. Includes right to privacy, clean environment, speedy trial, dignity, and livelihood."
    },
    "21a": {
        "title": "Right to Education",
        "part": "Part III: Fundamental Rights",
        "summary": "The State shall provide free and compulsory education to all children aged 6 to 14 years.",
        "significance": "Added by the 86th Amendment Act (2002), making elementary education a fundamental right."
    },
    "25": {
        "title": "Freedom of conscience and free profession of religion",
        "part": "Part III: Fundamental Rights",
        "summary": "All persons are equally entitled to freedom of conscience and the right freely to profess, practice, and propagate religion.",
        "significance": "Cornerstone of Indian secularism, subject to public order, morality, and health."
    },
    "32": {
        "title": "Remedies for enforcement of Fundamental Rights (Heart & Soul)",
        "part": "Part III: Fundamental Rights",
        "summary": "Guarantees the right to move the Supreme Court directly for the enforcement of Fundamental Rights via Constitutional Writs.",
        "significance": "Dr. B.R. Ambedkar called Article 32 the 'Heart and Soul of the Constitution'."
    },
    "44": {
        "title": "Uniform Civil Code (UCC)",
        "part": "Part IV: Directive Principles of State Policy (DPSP)",
        "summary": "The State shall endeavour to secure for the citizens a Uniform Civil Code throughout the territory of India.",
        "significance": "Non-justiciable directive principle aiming for a common set of civil personal laws regardless of religion."
    },
    "51a": {
        "title": "Fundamental Duties",
        "part": "Part IVA: Fundamental Duties",
        "summary": "Prescribes 11 moral obligations for citizens (e.g., abide by Constitution, respect National Flag & Anthem, protect sovereignty, preserve composite culture, safeguard public property).",
        "significance": "Added by 42nd Amendment (1976) on recommendations of the Swaran Singh Committee."
    },
    "72": {
        "title": "Pardoning powers of the President",
        "part": "Part V: The Union Executive",
        "summary": "Empowers the President to grant pardons, reprieves, respites, or remissions of punishment, or to suspend, remit, or commute sentences in all cases where punishment is by a Court Martial or is a death sentence.",
        "significance": "An executive grace power exercised on advice of the Council of Ministers, subject to limited judicial review against arbitrariness."
    },
    "124": {
        "title": "Establishment and Constitution of the Supreme Court",
        "part": "Part V: The Union Judiciary",
        "summary": "Establishes the Supreme Court of India, specifying appointment of Chief Justice and other Judges, tenure up to age 65, and removal by parliamentary impeachment.",
        "significance": "Guarantees judicial independence as part of the Basic Structure of the Constitution."
    },
    "142": {
        "title": "Enforcement of decrees and orders of Supreme Court (Complete Justice)",
        "part": "Part V: The Union Judiciary",
        "summary": "The Supreme Court in the exercise of its jurisdiction may pass such decree or make such order as is necessary for doing complete justice in any cause or matter pending before it.",
        "significance": "An extraordinary power invoked in landmark cases (e.g. Bhopal Gas tragedy, Ayodhya title suit, judicial reforms) to fill legislative vacuums."
    },
    "226": {
        "title": "Power of High Courts to issue certain writs",
        "part": "Part VI: The High Courts in the States",
        "summary": "Empowers High Courts to issue writs (Habeas Corpus, Mandamus, Prohibition, Quo Warranto, Certiorari) not just for Fundamental Rights, but for 'any other purpose' (legal rights).",
        "significance": "Writ jurisdiction of High Courts under Art 226 is actually wider in scope than the Supreme Court's under Art 32."
    },
    "300a": {
        "title": "Persons not to be deprived of property save by authority of law",
        "part": "Part XII: Finance, Property, Contracts and Suits",
        "summary": "No person shall be deprived of his property save by authority of law.",
        "significance": "Formerly a Fundamental Right under Art 31; converted into a Constitutional/Human Right by the 44th Amendment Act (1978)."
    },
    "324": {
        "title": "Superintendence, direction and control of elections in an Election Commission",
        "part": "Part XV: Elections",
        "summary": "Vests the superintendence, direction, and control of the preparation of electoral rolls and conduct of all elections to Parliament and State Legislatures in the Election Commission of India.",
        "significance": "Ensures free and fair elections, a core facet of democracy and basic structure."
    },
    "352": {
        "title": "Proclamation of National Emergency",
        "part": "Part XVIII: Emergency Provisions",
        "summary": "President can declare emergency if security of India is threatened by war, external aggression, or armed rebellion.",
        "significance": "Suspends fundamental freedoms under Art 19; centralizes federal power."
    },
    "356": {
        "title": "President's Rule (State Emergency)",
        "part": "Part XVIII: Emergency Provisions",
        "summary": "Allows imposition of President's Rule in a state if state constitutional machinery fails.",
        "significance": "Judicial review limits misuse (S.R. Bommai landmark case)."
    },
    "368": {
        "title": "Power of Parliament to amend the Constitution",
        "part": "Part XX: Amendment of the Constitution",
        "summary": "Sets out procedures to amend the Constitution by special majority.",
        "significance": "Cannot alter the 'Basic Structure' of the Constitution (Kesavananda Bharati case, 1973)."
    },
    "370": {
        "title": "Temporary provisions with respect to the State of Jammu and Kashmir",
        "part": "Part XXI: Temporary, Transitional and Special Provisions",
        "summary": "Historically granted autonomous special status to Jammu and Kashmir, allowing its own constitution and flag, with Parliament having limited law-making powers (defense, external affairs, communications).",
        "significance": "On August 5, 2019, the Government of India issued Presidential Orders (C.O. 272 & 273) and Parliament passed the J&K Reorganisation Act, effectively abrogating its special status and bifurcating the state into Union Territories (J&K and Ladakh). The Supreme Court upheld the constitutional validity in December 2023."
    },
    "12": {
        "title": "Definition of 'State'",
        "part": "Part III: Fundamental Rights",
        "summary": "Defines the State to include the Government and Parliament of India, the Government and Legislature of each of the States, and all local or other authorities within the territory of India or under the control of the Government of India.",
        "significance": "Determines against whom Fundamental Rights can be enforced."
    },
    "13": {
        "title": "Laws inconsistent with or in derogation of Fundamental Rights",
        "part": "Part III: Fundamental Rights",
        "summary": "Declares that all laws in force before the commencement of the Constitution, and any law made by the State thereafter, to the extent of inconsistency with Fundamental Rights, shall be void.",
        "significance": "The primary constitutional basis for Judicial Review and doctrines of Severability and Eclipse."
    },
    "16": {
        "title": "Equality of opportunity in matters of public employment",
        "part": "Part III: Fundamental Rights",
        "summary": "Guarantees equality of opportunity for all citizens in matters relating to employment or appointment to any office under the State.",
        "significance": "Allows reservations (Articles 16(4), 16(4A), 16(6)) for backward classes and EWS."
    },
    "20": {
        "title": "Protection in respect of conviction for offences",
        "part": "Part III: Fundamental Rights",
        "summary": "Provides three vital criminal protections: (1) Protection against ex-post facto laws, (2) Protection against Double Jeopardy, and (3) Protection against Self-Incrimination.",
        "significance": "Absolute right that cannot be suspended even during a National Emergency (Article 359)."
    },
    "22": {
        "title": "Protection against arrest and detention in certain cases",
        "part": "Part III: Fundamental Rights",
        "summary": "Guarantees rights of arrested persons: informed of grounds of arrest, right to consult legal counsel, and production before a magistrate within 24 hours. Also outlines preventive detention safeguards.",
        "significance": "Key procedural safeguard preventing arbitrary police custody."
    },
    "39a": {
        "title": "Equal justice and free legal aid",
        "part": "Part IV: Directive Principles of State Policy (DPSP)",
        "summary": "Mandates that the State shall secure equal justice and provide free legal aid to ensure opportunities for securing justice are not denied by reason of economic or other disabilities.",
        "significance": "Led to the Legal Services Authorities Act, 1987 (NALSA) and Lok Adalats."
    },
    "50": {
        "title": "Separation of judiciary from executive",
        "part": "Part IV: Directive Principles of State Policy (DPSP)",
        "summary": "The State shall take steps to separate the judiciary from the executive in the public services of the State.",
        "significance": "Foundational principle preserving independence and impartiality of the judicial system."
    },
    "136": {
        "title": "Special leave to appeal by the Supreme Court (SLP)",
        "part": "Part V: The Union Judiciary",
        "summary": "Empowers the Supreme Court to grant special leave to appeal from any judgment, decree, determination, sentence, or order in any cause or matter passed by any court or tribunal in India.",
        "significance": "A plenary discretionary power to correct grave miscarriage of justice."
    },
    "141": {
        "title": "Law declared by Supreme Court to be binding on all courts",
        "part": "Part V: The Union Judiciary",
        "summary": "The law declared by the Supreme Court shall be binding on all courts within the territory of India.",
        "significance": "Establishes the doctrine of Precedent (Stare Decisis) at the national level."
    },
    "143": {
        "title": "Power of President to consult Supreme Court (Advisory Jurisdiction)",
        "part": "Part V: The Union Judiciary",
        "summary": "The President may refer any question of law or fact of public importance to the Supreme Court for its advisory opinion.",
        "significance": "Advisory jurisdiction utilized on major national constitutional questions (e.g. Berubari, Ayodhya reference)."
    }
}

# --- 2B. LANDMARK SUPREME COURT CASES ---
CASES_DB = {
    "kesavananda bharati": {
        "citation": "Kesavananda Bharati v. State of Kerala (1973) 4 SCC 225",
        "bench": "13-Judge Constitution Bench (7:6 majority)",
        "doctrine": "Basic Structure Doctrine",
        "ruling": "Parliament's amending power under Article 368 is not unlimited; it cannot alter, destroy, or emasculate the Basic Structure of the Constitution (such as democracy, secularism, rule of law, federalism, judicial review).",
        "significance": "The most celebrated judgment in Indian constitutional history, preserving the democratic fabric."
    },
    "maneka gandhi": {
        "citation": "Maneka Gandhi v. Union of India (1978) 1 SCC 248",
        "bench": "7-Judge Bench",
        "doctrine": "Procedure Established by Law = Due Process of Law (Golden Triangle)",
        "ruling": "Article 21 must be read harmoniously with Articles 14 and 19 ('Golden Triangle'). Procedure depriving a person of life or personal liberty must be 'just, fair, and reasonable', not arbitrary, whimsical, or oppressive.",
        "significance": "Radically expanded personal liberty, birthed substantive due process in India, and enabled human rights jurisprudence."
    },
    "puttaswamy": {
        "citation": "Justice K.S. Puttaswamy (Retd.) v. Union of India (2017) 10 SCC 1",
        "bench": "9-Judge Constitution Bench (Unanimous 9:0)",
        "doctrine": "Fundamental Right to Privacy",
        "ruling": "Right to Privacy is a Fundamental Right guaranteed under Article 21 and Part III of the Constitution. Privacy includes informational privacy, bodily autonomy, and spatial privacy.",
        "significance": "Overruled MP Sharma (1954) and Kharak Singh (1962). Laid the legal bedrock for data protection laws, digital rights, and bodily autonomy."
    },
    "navtej johar": {
        "citation": "Navtej Singh Johar v. Union of India (2018) 10 SCC 1",
        "bench": "5-Judge Constitution Bench (Unanimous)",
        "doctrine": "Constitutional Morality & Decriminalization of Section 377 IPC",
        "ruling": "Consensual sexual intercourse between adults in private does not violate public morality. Section 377 IPC was read down to decriminalize LGBTQ+ relations, upholding Articles 14, 15, 19, and 21.",
        "significance": "Established Constitutional Morality over popular morality and recognized transformative constitutionalism."
    },
    "shayara bano": {
        "citation": "Shayara Bano v. Union of India (2017) 9 SCC 1",
        "bench": "5-Judge Multi-faith Constitution Bench (3:2 majority)",
        "doctrine": "Manifest Arbitrariness Doctrine under Article 14",
        "ruling": "Talaq-e-biddat (instant triple talaq) declared unconstitutional and void for being manifestly arbitrary and violating Muslim women's fundamental rights under Article 14.",
        "significance": "Established that subordinate and personal law customs violating Part III cannot claim immunity."
    },
    "sr bommai": {
        "citation": "S.R. Bommai v. Union of India (1994) 3 SCC 1",
        "bench": "9-Judge Constitution Bench",
        "doctrine": "Federalism and Secularism as Basic Structure; Judicial Review of Article 356",
        "ruling": "Imposition of President's Rule under Article 356 is subject to judicial review. Floor test is the only constitutional mechanism to prove a government's majority. Secularism is a core feature of the basic structure.",
        "significance": "Severely curbed the misuse of Article 356 by central governments against state legislatures."
    },
    "indira gandhi": {
        "citation": "Indira Nehru Gandhi v. Raj Narain (1975) Supp SCC 1",
        "bench": "5-Judge Constitution Bench",
        "doctrine": "Free & Fair Elections and Judicial Review as Basic Structure",
        "ruling": "Struck down the 39th Amendment (Article 329A(4)) which attempted to place the Prime Minister's election beyond judicial review.",
        "significance": "First application of Kesavananda Bharati doctrine to strike down a constitutional amendment."
    },
    "minerva mills": {
        "citation": "Minerva Mills Ltd. v. Union of India (1980) 3 SCC 625",
        "bench": "5-Judge Constitution Bench",
        "doctrine": "Harmonious Balance between Fundamental Rights and Directive Principles",
        "ruling": "Fundamental Rights and DPSP are two wheels of a chariot. Parliament cannot give blanket supremacy to DPSP over Fundamental Rights, nor can it remove judicial review.",
        "significance": "Reaffirmed the sanctity of the Basic Structure against Emergency-era 42nd Amendment clauses."
    }
}

# --- 3. WRITS & LEGAL TERMS ---
TERMS_DB = {
    "habeas corpus": (
        "Literal meaning: 'To have the body of'.\n"
        "A court order to produce a detained person before the court to examine whether the arrest is lawful. "
        "Protects individuals against unlawful detention."
    ),
    "mandamus": (
        "Literal meaning: 'We command'.\n"
        "Issued to a public official, government body, or lower court to compel them to perform an official legal duty they failed to do."
    ),
    "prohibition": (
        "Literal meaning: 'To forbid'.\n"
        "Issued by a higher court (Supreme Court/High Court) to a lower court to prevent it from exceeding its legal jurisdiction."
    ),
    "certiorari": (
        "Literal meaning: 'To be certified/informed'.\n"
        "Issued to quash an order already passed by a lower court or tribunal that acted without jurisdiction or violated natural justice."
    ),
    "quo warranto": (
        "Literal meaning: 'By what authority/warrant?'.\n"
        "Prevents illegal usurpation of a public office by directing the person to show under what authority they hold that office."
    ),
    "basic structure doctrine": (
        "Established by Supreme Court in Kesavananda Bharati (1973).\n"
        "Rules that while Parliament has wide powers to amend the Constitution under Article 368, it CANNOT destroy or alter its "
        "foundational principles (democracy, rule of law, judicial review, secularism, federalism)."
    ),
    "secularism": (
        "In the Indian constitutional context, secularism means 'Sarva Dharma Sambhava' (equal respect and treatment for all religions), "
        "where the State has no official state religion and does not discriminate based on faith."
    ),
    "judicial review": (
        "The power of the judiciary (Supreme Court & High Courts) to review legislative laws and executive orders, and declare them null and void "
        "if they violate constitutional provisions (Articles 13, 32, 226)."
    )
}

# --- 4. MAJOR AMENDMENTS ---
AMENDMENTS_DB = {
    "42": {
        "year": "1976",
        "nickname": "Mini-Constitution",
        "details": "Added words 'SOCIALIST', 'SECULAR', and 'INTEGRITY' to the Preamble. Added Fundamental Duties (Part IVA, Article 51A). Made fundamental changes across multiple articles during the Emergency."
    },
    "44": {
        "year": "1978",
        "nickname": "Right to Property amendment",
        "details": "Removed Right to Property from Fundamental Rights (Article 31) and made it a constitutional/legal right under Article 300A. Added safeguards against arbitrary emergencies."
    },
    "86": {
        "year": "2002",
        "nickname": "Right to Education amendment",
        "details": "Inserted Article 21A making free elementary education a fundamental right for children aged 6 to 14. Added 11th fundamental duty for parents under 51A(k)."
    },
    "101": {
        "year": "2016",
        "nickname": "Goods and Services Tax (GST)",
        "details": "Introduced nationwide uniform indirect taxation (GST) under Article 246A, 269A, and 279A, establishing the GST Council."
    }
}

# --- 5. QUIZ QUESTIONS ---
QUIZ_QUESTIONS = [
    {
        "question": "Which Article of the Indian Constitution is known as the 'Heart and Soul of the Constitution'?",
        "options": ["A) Article 14", "B) Article 19", "C) Article 21", "D) Article 32"],
        "answer": "D",
        "explanation": "Dr. B.R. Ambedkar called Article 32 (Right to Constitutional Remedies) the heart and soul because it empowers citizens to directly approach the Supreme Court if fundamental rights are violated."
    },
    {
        "question": "Which Constitutional Amendment added the words 'Secular' and 'Socialist' to the Preamble?",
        "options": ["A) 42nd Amendment (1976)", "B) 44th Amendment (1978)", "C) 86th Amendment (2002)", "D) 1st Amendment (1951)"],
        "answer": "A",
        "explanation": "The 42nd Amendment Act of 1976 (also known as the Mini-Constitution) added Socialist, Secular, and Integrity to the Preamble."
    },
    {
        "question": "Which writ is used to release a person who is unlawfully detained or arrested?",
        "options": ["A) Mandamus", "B) Habeas Corpus", "C) Quo Warranto", "D) Certiorari"],
        "answer": "B",
        "explanation": "Habeas Corpus literally means 'to have the body'. It directs the detaining authority to produce the prisoner in court."
    },
    {
        "question": "Right to Education was made a Fundamental Right under which Article?",
        "options": ["A) Article 15", "B) Article 21A", "C) Article 45", "D) Article 51A"],
        "answer": "B",
        "explanation": "Article 21A was inserted by the 86th Constitutional Amendment Act (2002) guaranteeing free elementary education for ages 6-14."
    }
]

# --- TOOL FUNCTIONS ---

def get_preamble() -> str:
    """Returns the full official text of the Preamble with explanation."""
    return f"📜 THE CONSTITUTION OF INDIA - PREAMBLE\n\n{PREAMBLE_TEXT}"


def lookup_article(query: str) -> str:
    """
    Looks up a constitutional article by number or concept.
    Example query: '21', 'article 19', 'equality', 'education', 'emergency'
    """
    clean_query = query.lower().replace("article", "").replace("art", "").strip()

    # Exact number match
    if clean_query in ARTICLES_DB:
        art = ARTICLES_DB[clean_query]
        return (
            f"📖 Article {clean_query.upper()}: {art['title']}\n"
            f"🏛️ {art['part']}\n"
            f"📝 Summary: {art['summary']}\n"
            f"💡 Significance: {art['significance']}"
        )

    # Keyword match in title or summary
    for num, art in ARTICLES_DB.items():
        if clean_query in art["title"].lower() or clean_query in art["summary"].lower() or clean_query in art["significance"].lower():
            return (
                f"📖 Article {num.upper()}: {art['title']}\n"
                f"🏛️ {art['part']}\n"
                f"📝 Summary: {art['summary']}\n"
                f"💡 Significance: {art['significance']}"
            )

    available = ", ".join([f"Art {k.upper()}" for k in sorted(ARTICLES_DB.keys(), key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))])
    return (
        f"Article '{query}' is not yet in the local offline dictionary.\n\n"
        f"💡 TO ANSWER ANY QUESTION OR ARTICLE:\n"
        f"Connect Google Gemini by typing 'key' in the terminal!\n\n"
        f"Currently indexed offline articles:\n{available}"
    )


def get_fundamental_rights_summary() -> str:
    """Returns a structured overview of the 6 Fundamental Rights in Part III."""
    return (
        "🇮🇳 FUNDAMENTAL RIGHTS (Part III, Articles 12 - 35)\n\n"
        "1. Right to Equality (Articles 14 - 18)\n"
        "   - Equality before law, prohibition of discrimination, abolition of untouchability.\n\n"
        "2. Right to Freedom (Articles 19 - 22)\n"
        "   - 6 democratic freedoms (speech, assembly), protection of life & liberty (Art 21), education (Art 21A).\n\n"
        "3. Right against Exploitation (Articles 23 - 24)\n"
        "   - Prohibition of human trafficking, forced labor, and child labor in hazardous factories.\n\n"
        "4. Right to Freedom of Religion (Articles 25 - 28)\n"
        "   - Freedom of conscience, free profession, practice, and propagation of religion.\n\n"
        "5. Cultural and Educational Rights (Articles 29 - 30)\n"
        "   - Protection of minority languages, script, culture, and right to establish educational institutions.\n\n"
        "6. Right to Constitutional Remedies (Article 32)\n"
        "   - Right to move the Supreme Court directly via Writs (Habeas Corpus, Mandamus, etc.)."
    )


def lookup_legal_term(term: str) -> str:
    """
    Explains constitutional terminology, writs, and landmark legal doctrines.
    Example terms: 'habeas corpus', 'mandamus', 'basic structure', 'secularism'
    """
    clean_term = term.strip().lower()
    for key, explanation in TERMS_DB.items():
        if key in clean_term or clean_term in key:
            return f"⚖️ Legal Concept: [{key.upper()}]\n{explanation}"

    return f"Term '{term}' not found. Try one of: {', '.join(TERMS_DB.keys())}."


def lookup_amendment(query: str) -> str:
    """
    Looks up constitutional amendments.
    Example: '42', 'amendment 44', 'education', 'gst'
    """
    clean = query.lower().replace("amendment", "").replace("st", "").replace("nd", "").replace("rd", "").replace("th", "").strip()

    # Exact number
    if clean in AMENDMENTS_DB:
        amd = AMENDMENTS_DB[clean]
        return (
            f"📜 {clean}th Constitutional Amendment Act ({amd['year']})\n"
            f"🏷️ Popular Name: {amd['nickname']}\n"
            f"📝 Highlights: {amd['details']}"
        )

    # Keyword match
    for num, amd in AMENDMENTS_DB.items():
        if clean in amd["nickname"].lower() or clean in amd["details"].lower():
            return (
                f"📜 {num}th Constitutional Amendment Act ({amd['year']})\n"
                f"🏷️ Popular Name: {amd['nickname']}\n"
                f"📝 Highlights: {amd['details']}"
            )

    return f"Amendment '{query}' not found. Try: 42 (Mini-Constitution), 44 (Property), 86 (Education), 101 (GST)."


def lookup_landmark_case(query: str) -> str:
    """
    Looks up landmark Supreme Court judgments by case name or legal doctrine.
    Example query: 'kesavananda bharati', 'maneka gandhi', 'puttaswamy', 'privacy', 'triple talaq'
    """
    clean_q = query.lower().strip()
    
    # Check exact/partial key match
    for key, c in CASES_DB.items():
        if key in clean_q or clean_q in key or clean_q in c["citation"].lower() or clean_q in c["doctrine"].lower():
            return (
                f"🏛️ Landmark Case: {c['citation']}\n"
                f"⚖️ Bench: {c['bench']}\n"
                f"📜 Core Doctrine: {c['doctrine']}\n"
                f"📋 Key Ruling: {c['ruling']}\n"
                f"💡 Constitutional Significance: {c['significance']}"
            )
            
    # Check words
    for key, c in CASES_DB.items():
        for word in clean_q.split():
            if len(word) > 3 and (word in c["doctrine"].lower() or word in c["ruling"].lower() or word in c["significance"].lower()):
                return (
                    f"🏛️ Landmark Case: {c['citation']}\n"
                    f"⚖️ Bench: {c['bench']}\n"
                    f"📜 Core Doctrine: {c['doctrine']}\n"
                    f"📋 Key Ruling: {c['ruling']}\n"
                    f"💡 Constitutional Significance: {c['significance']}"
                )

    cases_list = ", ".join([c["citation"].split(" (")[0] for c in CASES_DB.values()])
    return f"Case '{query}' not found in local index. Key indexed cases include: {cases_list}."


def search_legal_knowledge_base(query: str) -> Dict[str, Any]:
    """
    Intelligent unified search across the entire Constitutional Knowledge Base:
    Articles, Landmark Cases, Writs, and Amendments.
    """
    q = query.lower().strip()
    results = {
        "articles": [],
        "cases": [],
        "terms": [],
        "amendments": [],
        "preamble_matched": False
    }

    # Preamble check
    if any(k in q for k in ["preamble", "we the people", "sovereign socialist secular", "fraternity"]):
        results["preamble_matched"] = True

    # Articles check
    for num, art in ARTICLES_DB.items():
        if f"art {num}" in q or f"article {num}" in q or (q.isdigit() and q == num) or (len(num) > 1 and f" {num} " in f" {q} "):
            results["articles"].append({"article": num.upper(), **art})
        elif any(term in art["title"].lower() or term in art["summary"].lower() for term in q.split() if len(term) > 3):
            if {"article": num.upper(), **art} not in results["articles"]:
                results["articles"].append({"article": num.upper(), **art})

    # Landmark cases check
    for key, c in CASES_DB.items():
        if key in q or any(term in c["citation"].lower() or term in c["doctrine"].lower() for term in q.split() if len(term) > 3):
            results["cases"].append(c)

    # Writs & Terms check
    for term, exp in TERMS_DB.items():
        if term in q:
            results["terms"].append({"term": term.upper(), "explanation": exp})

    # Amendments check
    for num, amd in AMENDMENTS_DB.items():
        if f"{num}th" in q or f"amendment {num}" in q or f"{num} amendment" in q:
            results["amendments"].append({"number": num, **amd})

    return results


def get_random_quiz() -> Dict[str, Any]:
    """Returns a random constitutional quiz item."""
    import random
    return random.choice(QUIZ_QUESTIONS)


# Registry of tools available to the Constitutional Agent
CONSTITUTION_TOOLS = {
    "get_preamble": {
        "function": get_preamble,
        "description": "Returns the complete text and preamble principles of the Constitution."
    },
    "lookup_article": {
        "function": lookup_article,
        "description": "Looks up a specific constitutional article by number (e.g. 14, 19, 21, 32, 356) or keyword."
    },
    "lookup_landmark_case": {
        "function": lookup_landmark_case,
        "description": "Retrieves landmark Supreme Court judgements and doctrines (e.g., Kesavananda Bharati, Maneka Gandhi, Puttaswamy, Navtej Johar, Shayara Bano, Bommai)."
    },
    "get_fundamental_rights_summary": {
        "function": get_fundamental_rights_summary,
        "description": "Provides an organized overview of the 6 Fundamental Rights (Part III)."
    },
    "lookup_legal_term": {
        "function": lookup_legal_term,
        "description": "Explains legal doctrines and writs like Habeas Corpus, Mandamus, Basic Structure Doctrine."
    },
    "lookup_amendment": {
        "function": lookup_amendment,
        "description": "Provides information about constitutional amendments (42nd, 44th, 86th, 101st)."
    },
    "search_legal_knowledge_base": {
        "function": search_legal_knowledge_base,
        "description": "Comprehensive search across articles, cases, writs, and amendments in the constitutional knowledge base."
    }
}
