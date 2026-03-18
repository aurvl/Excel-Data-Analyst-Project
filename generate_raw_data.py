from pathlib import Path
import random
import pandas as pd
import numpy as np

UNCLEAN_RATE = 0.15
SEED = 42

random.seed(SEED)
np.random.seed(SEED)

OUTPUT_DIR = Path("raw_data")
OUTPUT_DIR.mkdir(exist_ok=True)

YEAR = 2025

first_names = [
    "Jerome","Nicolas","Sophie","Camille","Thomas","Lucie","Antoine","Sarah","Julie","Maxime",
    "Karim","Nadia","Mehdi","Lea","Emma","Louis","Paul","Chloe","Ines","Yassine",
    "Mariam","Fatou","Aurelien","Hugo","Clara","Morgane","Kevin","Noemie","Benoit","Laura",
    "Romain","Celine","Dylan","Elodie","Brahim","Salome","Ahmed","Aicha","Florian","Jade"
]

last_names = [
    "Martin","Bernard","Dubois","Thomas","Robert","Richard","Petit","Durand","Leroy","Moreau",
    "Simon","Laurent","Michel","Garcia","David","Bertrand","Roux","Vincent","Fournier","Morel",
    "Girard","Andre","Lefevre","Mercier","Dupont","Lambert","Bonnet","Francois","Martinez","Legrand",
    "Diop","Traore","Konate","Sow","Diallo","Bamba","Lopez","Garnier","Chevalier","Faure"
]

companies = [
    "Azur Concept","Nova Retail","Bati Plus","Hexa Services","Delta Market","Riviera Supply",
    "Urban Motion","Atlas Trading","Prestige Home","Optima Conseil","Soleil Distribution",
    "Mediterra Shop","Blue Horizon","Cap Sud Equipement","Alpha Partners","Vision Commerce",
    "Kora Logistics","Elite Habitat","Smart Office","Topline Solutions"
]

regions = {
    "France": ["Ile-de-France","PACA","Auvergne-Rhone-Alpes","Occitanie","Nouvelle-Aquitaine","Grand Est"],
    "Belgique": ["Bruxelles","Wallonie","Flandre"],
    "Espagne": ["Catalogne","Madrid","Andalousie"],
    "Maroc": ["Casablanca-Settat","Rabat-Sale-Kenitra","Marrakech-Safi"],
    "Cote dIvoire": ["Abidjan","Yamoussoukro","Bouake"]
}

segments = ["B2C","B2B PME","B2B Grand Compte"]
channels = ["E-commerce","Retail","Inside Sales"]

payment_terms_map = {
    "B2C": "CB - comptant",
    "B2B PME": "30 jours",
    "B2B Grand Compte": "45 jours"
}

products = pd.DataFrame([
    ["P001","Laptop 14 Pro","Electronics","Tech",1190,760],
    ["P002","Smartphone X5","Electronics","Tech",849,520],
    ["P003","Tablette Air 11","Electronics","Tech",629,395],
    ["P004","Casque Audio Max","Electronics","Tech",179,86],
    ["P005","Ecran 27 pouces","Electronics","Tech",299,182],
    ["P006","Clavier Meca","Electronics","Tech",109,54],
    ["P007","Chaussures City","Fashion","Lifestyle",95,39],
    ["P008","T-Shirt Essential","Fashion","Lifestyle",24,8],
    ["P009","Veste Urban","Fashion","Lifestyle",139,63],
    ["P010","Sac a dos Metro","Fashion","Lifestyle",74,31],
    ["P011","Chaise Ergo","Home","Home",215,124],
    ["P012","Lampe LED Desk","Home","Home",44,18],
], columns=["product_id","product_name","category","business_unit","list_price","standard_cost"])

# =========================================================
# 1. CUSTOMERS
# =========================================================
customer_rows = []
used_names = set()

for i in range(1, 181):
    cust_type = np.random.choice(["person", "company"], p=[0.58, 0.42])

    if cust_type == "person":
        while True:
            full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            if full_name not in used_names:
                used_names.add(full_name)
                break
        customer_name = full_name
    else:
        customer_name = f"{random.choice(companies)} {np.random.choice(['SARL','SAS','Group','Holding','Services'])}"

    country = np.random.choice(list(regions.keys()), p=[0.55, 0.08, 0.10, 0.12, 0.15])
    region = random.choice(regions[country])
    segment = np.random.choice(segments, p=[0.45, 0.38, 0.17])
    payment_terms = payment_terms_map[segment]

    customer_rows.append([
        f"C{i:04d}", customer_name, country, region, segment, payment_terms
    ])

customers = pd.DataFrame(customer_rows, columns=[
    "customer_id","customer_name","country","region","segment","payment_terms"
])

# =========================================================
# 2. SALES ORDERS + SALES LINES
# =========================================================
dates = pd.date_range(f"{YEAR}-01-01", f"{YEAR}-12-31", freq="D")
base_orders_per_month = {
    1:95, 2:105, 3:115, 4:120, 5:128, 6:135,
    7:142, 8:150, 9:132, 10:146, 11:175, 12:190
}

sales_orders = []
sales_lines = []
order_idx = 1
line_idx = 1

for month in range(1, 13):
    month_dates = dates[dates.month == month]
    n_orders = base_orders_per_month[month]

    for _ in range(n_orders):
        order_date = pd.Timestamp(np.random.choice(month_dates))
        customer = customers.sample(1, random_state=np.random.randint(0, 1_000_000)).iloc[0]
        channel = np.random.choice(channels, p=[0.47, 0.31, 0.22])
        order_id = f"SO{order_idx:06d}"

        sales_orders.append([
            order_id,
            order_date.date().isoformat(),
            customer["customer_id"],
            customer["customer_name"],
            channel,
            customer["payment_terms"],
            "EUR"
        ])

        n_lines = np.random.choice([1, 2, 3], p=[0.70, 0.24, 0.06])

        for __ in range(n_lines):
            product = products.sample(1, random_state=np.random.randint(0, 1_000_000)).iloc[0]

            if channel == "Inside Sales":
                qty = np.random.randint(3, 14) if product["category"] != "Fashion" else np.random.randint(6, 24)
            elif channel == "Retail":
                qty = np.random.randint(1, 5) if product["category"] != "Fashion" else np.random.randint(1, 7)
            else:
                qty = np.random.randint(1, 4) if product["category"] != "Fashion" else np.random.randint(1, 5)

            if channel == "Inside Sales":
                factor = np.random.uniform(0.86, 0.93)
            elif channel == "Retail":
                factor = np.random.uniform(0.98, 1.04)
            else:
                factor = np.random.uniform(0.94, 1.02)

            unit_selling_price = round(product["list_price"] * factor, 2)

            if customer["segment"] == "B2C":
                discount_pct = np.random.choice([0, 0, 0, 5, 10], p=[0.35, 0.25, 0.15, 0.15, 0.10])
            elif customer["segment"] == "B2B PME":
                discount_pct = np.random.choice([0, 5, 8, 10, 12], p=[0.10, 0.28, 0.26, 0.24, 0.12])
            else:
                discount_pct = np.random.choice([5, 8, 10, 12, 15], p=[0.16, 0.24, 0.26, 0.20, 0.14])

            sales_lines.append([
                f"SOL{line_idx:07d}",
                order_id,
                product["product_id"],
                product["product_name"],
                qty,
                unit_selling_price,
                discount_pct,
                product["standard_cost"]
            ])

            line_idx += 1

        order_idx += 1

sales_orders = pd.DataFrame(sales_orders, columns=[
    "order_id","order_date","customer_id","customer_name","channel","payment_terms","currency"
])

sales_lines = pd.DataFrame(sales_lines, columns=[
    "sales_line_id","order_id","product_id","product_name","quantity",
    "unit_selling_price","discount_pct","standard_cost"
])

# =========================================================
# 3. OPERATING EXPENSES
# =========================================================
vendors = {
    "Rent": ["SCI Riviera Immo"],
    "Payroll": ["Cabinet Paye Sud"],
    "Marketing": ["Meta Ads","Google Ads","Agence Pulse","TikTok Ads"],
    "Software": ["Microsoft","Adobe","Notion","HubSpot","OVHcloud"],
    "Logistics": ["DHL","Chronopost","UPS","FedEx"],
    "Travel": ["SNCF","Air France","Booking Business"],
    "Utilities": ["EDF","Orange Business","Veolia"],
    "Professional Fees": ["Cabinet Audit Conseil","Legal Partners","Compta Expert"],
    "Office": ["Bureau Vallee","Office Depot"]
}

expense_rows = []
expense_idx = 1

for month in range(1, 13):
    month_dates = dates[dates.month == month]

    rent_date = pd.Timestamp(np.random.choice(month_dates[:5]))
    expense_rows.append([
        f"EXP{expense_idx:06d}", rent_date.date().isoformat(), "Rent", "General & Admin",
        "SCI Riviera Immo", round(np.random.uniform(17500, 18500), 2), "EUR"
    ])
    expense_idx += 1

    payroll_date = pd.Timestamp(np.random.choice(month_dates[20:28]))
    expense_rows.append([
        f"EXP{expense_idx:06d}", payroll_date.date().isoformat(), "Payroll", "HR",
        "Cabinet Paye Sud", round(np.random.uniform(108000, 122000), 2), "EUR"
    ])
    expense_idx += 1

    for _ in range(np.random.randint(3, 6)):
        d = pd.Timestamp(np.random.choice(month_dates))
        expense_rows.append([
            f"EXP{expense_idx:06d}", d.date().isoformat(), "Software", "IT",
            random.choice(vendors["Software"]), round(np.random.uniform(250, 2800), 2), "EUR"
        ])
        expense_idx += 1

    for _ in range(np.random.randint(6, 11)):
        d = pd.Timestamp(np.random.choice(month_dates))
        expense_rows.append([
            f"EXP{expense_idx:06d}", d.date().isoformat(), "Marketing", "Sales & Marketing",
            random.choice(vendors["Marketing"]), round(np.random.uniform(900, 9500), 2), "EUR"
        ])
        expense_idx += 1

    for _ in range(np.random.randint(8, 16)):
        d = pd.Timestamp(np.random.choice(month_dates))
        expense_rows.append([
            f"EXP{expense_idx:06d}", d.date().isoformat(), "Logistics", "Operations",
            random.choice(vendors["Logistics"]), round(np.random.uniform(120, 2400), 2), "EUR"
        ])
        expense_idx += 1

    other_types = ["Utilities", "Office", "Professional Fees", "Travel"]
    for _ in range(np.random.randint(6, 12)):
        typ = random.choice(other_types)
        dept = {
            "Utilities": "General & Admin",
            "Office": "General & Admin",
            "Professional Fees": "Finance",
            "Travel": "Sales & Marketing"
        }[typ]
        d = pd.Timestamp(np.random.choice(month_dates))
        expense_rows.append([
            f"EXP{expense_idx:06d}", d.date().isoformat(), typ, dept,
            random.choice(vendors[typ]), round(np.random.uniform(80, 4200), 2), "EUR"
        ])
        expense_idx += 1

operating_expenses = pd.DataFrame(expense_rows, columns=[
    "expense_id","expense_date","expense_type","department","vendor_name","amount","currency"
])

# =========================================================
# 4. BUDGET
# =========================================================
budget_rows = []
seasonality = {
    1:0.88, 2:0.92, 3:0.98, 4:1.00, 5:1.02, 6:1.05,
    7:1.08, 8:1.10, 9:1.00, 10:1.08, 11:1.22, 12:1.30
}

for month in range(1, 13):
    month_start = pd.Timestamp(f"{YEAR}-{month:02d}-01")
    factor = seasonality[month]
    budget_rows.append([
        month_start.strftime("%Y-%m"),
        round(210000 * factor * np.random.uniform(0.95, 1.08), 2),
        round(125000 * factor * np.random.uniform(0.94, 1.06), 2),
        round(175000 * np.random.uniform(0.97, 1.04), 2),
        round(np.random.uniform(1150000, 1350000), 2) if month == 1 else None
    ])

budget_monthly = pd.DataFrame(budget_rows, columns=[
    "year_month","budget_revenue","budget_cogs","budget_opex","budget_opening_cash"
])

# =========================================================
# 5. OPENING CASH
# =========================================================
opening_cash = pd.DataFrame([
    ["2025-01-01", 1235000.00]
], columns=["as_of_date","opening_cash"])

# =========================================================
# 6. BANK TRANSACTIONS
# =========================================================
orders_for_cash = sales_orders.merge(
    customers[["customer_id","segment"]],
    on="customer_id",
    how="left"
)

order_values = sales_lines.copy()
order_values["gross_line_amount"] = order_values["quantity"] * order_values["unit_selling_price"]
order_values["net_line_amount"] = order_values["gross_line_amount"] * (1 - order_values["discount_pct"] / 100)
order_values = order_values.groupby("order_id", as_index=False)["net_line_amount"].sum()

receipts = orders_for_cash.merge(order_values, on="order_id", how="left")
receipts["order_date"] = pd.to_datetime(receipts["order_date"], errors="coerce")

def payment_delay(terms):
    terms = str(terms)
    if "comptant" in terms.lower():
        return np.random.randint(0, 3)
    if "30" in terms:
        return np.random.randint(26, 38)
    return np.random.randint(40, 52)

bank_rows = []
bank_idx = 1

for _, row in receipts.iterrows():
    pay_date = row["order_date"] + pd.Timedelta(days=int(payment_delay(row["payment_terms"])))
    bank_rows.append([
        f"BNK{bank_idx:07d}",
        pay_date.date().isoformat(),
        "Customer Receipt",
        "Inflow",
        row["customer_name"],
        round(row["net_line_amount"], 2),
        "EUR"
    ])
    bank_idx += 1

for _, row in operating_expenses.iterrows():
    expense_date = pd.to_datetime(row["expense_date"], errors="coerce")
    delay = np.random.randint(0, 4) if row["expense_type"] in ["Rent","Payroll","Utilities"] else np.random.randint(7, 25)
    pay_date = expense_date + pd.Timedelta(days=int(delay))
    bank_rows.append([
        f"BNK{bank_idx:07d}",
        pay_date.date().isoformat(),
        row["expense_type"] + " Payment",
        "Outflow",
        row["vendor_name"],
        round(row["amount"], 2),
        "EUR"
    ])
    bank_idx += 1

for month in [2, 5, 9, 11]:
    d = pd.Timestamp(f"{YEAR}-{month:02d}-{np.random.randint(5, 24):02d}")
    bank_rows.append([
        f"BNK{bank_idx:07d}",
        d.date().isoformat(),
        "Capex",
        "Outflow",
        random.choice(["Dell Business","Apple Business","HP Pro","Ikea Pro"]),
        round(np.random.uniform(9000, 28000), 2),
        "EUR"
    ])
    bank_idx += 1

bank_transactions = pd.DataFrame(bank_rows, columns=[
    "bank_txn_id","transaction_date","transaction_type","flow_direction","counterparty","amount","currency"
])

# =========================================================
# 7. CALENDAR
# =========================================================
calendar = pd.DataFrame({"date": pd.date_range(f"{YEAR}-01-01", f"{YEAR}-12-31", freq="D")})
calendar["year"] = calendar["date"].dt.year
calendar["month_num"] = calendar["date"].dt.month
calendar["month_name"] = calendar["date"].dt.strftime("%B")
calendar["quarter"] = "Q" + calendar["date"].dt.quarter.astype(str)
calendar["year_month"] = calendar["date"].dt.strftime("%Y-%m")

# =========================================================
# 8. DIRTY FUNCTIONS
# =========================================================
def random_date_format(dt_value):
    if pd.isna(dt_value):
        return dt_value

    dt = pd.to_datetime(dt_value, errors="coerce")
    if pd.isna(dt):
        return dt_value

    formats = [
        dt.strftime("%Y-%m-%d"),
        dt.strftime("%d/%m/%Y"),
        dt.strftime("%m-%d-%Y"),
        dt.strftime("%d-%m-%Y"),
    ]
    return random.choice(formats)

def dirty_string(value):
    if pd.isna(value):
        return value

    value = str(value)

    transformations = [
        lambda x: " " + x,
        lambda x: x + " ",
        lambda x: "  " + x + "  ",
        lambda x: x.upper(),
        lambda x: x.lower(),
        lambda x: x.title(),
        lambda x: x.replace(" ", "  "),
    ]
    return random.choice(transformations)(value)

def dirty_numeric(value):
    if pd.isna(value):
        return value

    try:
        clean_value = float(str(value).replace(",", ".").strip())
    except ValueError:
        return value

    choice = random.choice(["string_comma", "string_space", "rounded", "normal"])
    if choice == "string_comma":
        return str(round(clean_value, 2)).replace(".", ",")
    elif choice == "string_space":
        return f" {round(clean_value, 2)} "
    elif choice == "rounded":
        return round(clean_value, 0)
    return clean_value

def inject_missing(value, prob=0.25):
    if random.random() < prob:
        return random.choice([None, "", "NA", "N/A"])
    return value

def inject_typo(value, mapping):
    if pd.isna(value):
        return value
    value = str(value)
    if value in mapping:
        return random.choice(mapping[value])
    return value

def make_unclean(df, table_name, dirty_rate=0.20):
    df = df.copy().astype(object)

    n_rows = len(df)
    n_dirty = max(1, int(n_rows * dirty_rate))
    dirty_indices = np.random.choice(df.index, size=n_dirty, replace=False)

    typo_maps = {
        "country": {
            "France": ["france", "FRANCE", " France ", "Frnace"],
            "Belgique": ["belgique", "Belgique ", "BELGIQUE"],
            "Espagne": ["espagne", "Espana", "ESPAGNE"],
            "Maroc": ["maroc", "MAROC", " Maroc "],
            "Cote dIvoire": ["cote divoire", "Côte d'Ivoire", "Cote d Ivoire"]
        },
        "region": {
            "PACA": ["paca", "Paca", " PACA "],
            "Ile-de-France": ["ile de france", "Ile de France", "ILE-DE-FRANCE"],
            "Abidjan": ["abidjan", " Abidjan "],
            "Bruxelles": ["bruxelles", "Bruxelle"]
        },
        "channel": {
            "E-commerce": ["e-commerce", "Ecommerce", "E Commerce"],
            "Retail": ["retail", "Retail "],
            "Inside Sales": ["inside sales", "InsideSales", "Inside  Sales"]
        },
        "segment": {
            "B2C": ["b2c", "B2c", " B2C "],
            "B2B PME": ["b2b pme", "B2B-PME", "B2B PME "],
            "B2B Grand Compte": ["b2b grand compte", "Grand Compte", "B2B Grand  Compte"]
        },
        "expense_type": {
            "Rent": ["rent", " RENT ", "Rant"],
            "Payroll": ["payroll", "Pay roll"],
            "Marketing": ["marketing", "Marketng"],
            "Logistics": ["logistics", "Logistic"],
            "Software": ["software", "Softwares"]
        },
        "currency": {
            "EUR": ["eur", " Eur ", "EURO"]
        }
    }

    numeric_cols = [
        "quantity", "unit_selling_price", "discount_pct", "standard_cost", "amount",
        "budget_revenue", "budget_cogs", "budget_opex", "budget_opening_cash", "opening_cash",
        "list_price"
    ]

    text_cols = ["customer_name", "product_name", "vendor_name", "counterparty", "payment_terms"]

    for idx in dirty_indices:
        n_changes = random.randint(1, 3)

        for _ in range(n_changes):
            col = random.choice(df.columns.tolist())
            current_value = df.at[idx, col]

            if "date" in col.lower():
                if random.random() < 0.7:
                    df.at[idx, col] = random_date_format(current_value)
                else:
                    df.at[idx, col] = inject_missing(current_value, prob=0.5)

            elif col.endswith("_id"):
                if random.random() < 0.5:
                    df.at[idx, col] = dirty_string(current_value)

            elif col in text_cols:
                if random.random() < 0.75:
                    df.at[idx, col] = dirty_string(current_value)
                else:
                    df.at[idx, col] = inject_missing(current_value, prob=0.35)

            elif col in typo_maps:
                if random.random() < 0.75:
                    df.at[idx, col] = inject_typo(current_value, typo_maps[col])
                else:
                    df.at[idx, col] = inject_missing(current_value, prob=0.30)

            elif col in numeric_cols:
                if random.random() < 0.7:
                    df.at[idx, col] = dirty_numeric(current_value)
                else:
                    df.at[idx, col] = inject_missing(current_value, prob=0.25)

    if table_name in ["customers", "sales_orders", "sales_order_lines", "operating_expenses"]:
        dup_count = max(1, int(len(df) * 0.02))
        dup_sample = df.sample(dup_count, random_state=SEED)
        df = pd.concat([df, dup_sample], ignore_index=True)

    return df

# =========================================================
# 9. APPLY DIRTINESS
# =========================================================
customers_dirty = make_unclean(customers, "customers", dirty_rate=UNCLEAN_RATE)
products_dirty = make_unclean(products, "products", dirty_rate=UNCLEAN_RATE)
sales_orders_dirty = make_unclean(sales_orders, "sales_orders", dirty_rate=UNCLEAN_RATE)
sales_lines_dirty = make_unclean(sales_lines, "sales_order_lines", dirty_rate=UNCLEAN_RATE)
operating_expenses_dirty = make_unclean(operating_expenses, "operating_expenses", dirty_rate=UNCLEAN_RATE)
budget_monthly_dirty = make_unclean(budget_monthly, "budget_monthly", dirty_rate=UNCLEAN_RATE)
opening_cash_dirty = make_unclean(opening_cash, "opening_cash", dirty_rate=UNCLEAN_RATE)
bank_transactions_dirty = make_unclean(bank_transactions, "bank_transactions", dirty_rate=UNCLEAN_RATE)

# Je conseille de laisser calendar propre ou très peu sale
calendar_dirty = calendar.copy()

# =========================================================
# 10. EXPORT
# =========================================================
customers_dirty.to_csv(OUTPUT_DIR / "customers.csv", index=False)
products_dirty.to_csv(OUTPUT_DIR / "products.csv", index=False)
sales_orders_dirty.to_csv(OUTPUT_DIR / "sales_orders.csv", index=False)
sales_lines_dirty.to_csv(OUTPUT_DIR / "sales_order_lines.csv", index=False)
operating_expenses_dirty.to_csv(OUTPUT_DIR / "operating_expenses.csv", index=False)
budget_monthly_dirty.to_csv(OUTPUT_DIR / "budget_monthly.csv", index=False)
opening_cash_dirty.to_csv(OUTPUT_DIR / "opening_cash.csv", index=False)
bank_transactions_dirty.to_csv(OUTPUT_DIR / "bank_transactions.csv", index=False)
calendar_dirty.to_csv(OUTPUT_DIR / "calendar.csv", index=False)

guide = '''FICHIERS GENERES
- customers.csv : référentiel clients
- products.csv : référentiel produits avec prix catalogue et coût standard
- sales_orders.csv : entêtes de commandes
- sales_order_lines.csv : lignes de commandes
- operating_expenses.csv : dépenses d'exploitation brutes
- budget_monthly.csv : budget mensuel brut
- opening_cash.csv : solde d'ouverture de trésorerie
- bank_transactions.csv : mouvements bancaires bruts
- calendar.csv : calendrier

A CALCULER TOI-MEME DANS EXCEL
1. Chiffre d'affaires net = quantity * unit_selling_price * (1 - discount_pct)
2. COGS = quantity * standard_cost
3. Gross Profit = Revenue - COGS
4. OPEX mensuel = somme des operating_expenses par mois
5. Net Income = Gross Profit - OPEX
6. Cash Flow = inflows - outflows par mois
7. Ending Cash = opening cash + cumul des cash flows
8. Comparaisons vs budget et vs période précédente
'''
(OUTPUT_DIR / "README.txt").write_text(guide, encoding="utf-8")

print(f"Données brutes générées dans : {OUTPUT_DIR.resolve()}")
for p in sorted(OUTPUT_DIR.glob("*")):
    print("-", p.name)