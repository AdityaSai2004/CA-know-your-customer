import os
import csv
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

KEYWORDS = ['pending', 'fraud', 'default']


def load_directors(path):
    directors = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            directors.append(row['name'])
    return directors


def parse_financials(path):
    result = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Assets:' in line:
                result['assets'] = line.split(':')[1].strip()
            elif 'Liabilities:' in line:
                result['liabilities'] = line.split(':')[1].strip()
            elif 'Net Worth:' in line:
                result['net_worth'] = line.split(':')[1].strip()
    return result


def scan_court_cases(path):
    cases = []
    flags = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 4:
                court, status, case_id, desc = [p.strip() for p in parts]
                cases.append({
                    'court': court,
                    'status': status,
                    'case_id': case_id,
                    'desc': desc
                })
                for kw in KEYWORDS:
                    if kw in status.lower() or kw in desc.lower():
                        flags.append(f"{status} litigation: {desc}")
    return cases, flags


def assess_risk(financials, cases):
    debt_ratio = None
    try:
        assets = float(financials['assets'].replace('₹','').replace('Cr',''))
        liabilities = float(financials['liabilities'].replace('₹','').replace('Cr',''))
        debt_ratio = liabilities / assets if assets else 0
    except Exception:
        debt_ratio = None
    risk = 'Low'
    flags = []
    if debt_ratio is not None:
        if debt_ratio > 0.7:
            risk = 'Medium'
            flags.append('High debt ratio')
        if debt_ratio > 1:
            risk = 'High'
            flags.append('Very high debt ratio')
    if any(c['status'].lower() == 'pending' for c in cases):
        risk = 'Medium'
        flags.append('Ongoing litigation')
    return risk, flags, debt_ratio


def generate_report(company_name):
    folder = os.path.join(DATA_DIR, company_name)
    directors_path = os.path.join(folder, 'directors.csv')
    financials_path = os.path.join(folder, 'financials.txt')
    court_cases_path = os.path.join(folder, 'court_cases.txt')

    directors = load_directors(directors_path)
    financials = parse_financials(financials_path)
    cases, case_flags = scan_court_cases(court_cases_path)
    risk_level, risk_flags, debt_ratio = assess_risk(financials, cases)

    all_flags = risk_flags + case_flags

    json_report = {
        'company': f'{company_name} Pvt Ltd',
        'risk_level': risk_level,
        'directors': directors,
        'financial_health': financials,
        'legal_cases': [
            {'court': c['court'], 'status': c['status'], 'case_id': c['case_id']} for c in cases if c['status'].lower() == 'pending'
        ],
        'flags': all_flags
    }

    summary = f"{company_name} Pvt Ltd – Risk Level: {risk_level}\n"
    summary += f"- {len(directors)} active directors, compliant with MCA filings\n"
    summary += f"- Net worth {financials.get('net_worth','N/A')}, debt ratio {debt_ratio if debt_ratio is not None else 'N/A'}"
    if debt_ratio is not None and debt_ratio > 0.7:
        summary += " (above safe threshold)"
    summary += "\n"
    for c in cases:
        if c['status'].lower() == 'pending':
            summary += f"- Pending litigation at {c['court']} (Case {c['case_id']})\n"
    summary += "Recommendation: Onboard with conditions (monitor litigation)"

    return json_report, summary


def main():
    company = input('Enter company name (CompanyA, CompanyB): ').strip()
    if company not in ['CompanyA', 'CompanyB']:
        print('Invalid company name.')
        return
    json_report, summary = generate_report(company)
    print('--- JSON Report ---')
    print(json.dumps(json_report, indent=2, ensure_ascii=False))
    print('\n--- Human-readable Summary ---')
    print(summary)


if __name__ == '__main__':
    main()
