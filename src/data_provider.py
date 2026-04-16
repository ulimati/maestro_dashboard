from src.db import test_results

def get_metrics_for_platform(platform: str):
    """
    Agreguje data z MongoDB pro konkrétní platformu.
    Vypočítává metriky pro dashboard a připravuje data pro grafy.
    """
    # Vyhledávání v DB s ignorováním velikosti písmen
    query = {"platform": {"$regex": f"^{platform}$", "$options": "i"}}
    
    # Získáme výsledky z databáze jako list
    results = list(test_results.find(query))
    
    total = len(results)
    passed = sum(1 for r in results if r.get("status", "").lower() == "passed")
    failed = sum(1 for r in results if r.get("status", "").lower() == "failed")
    
    durations = [r.get("duration", 0) for r in results]
    avg_duration = sum(durations) / total if total > 0 else 0
    pass_rate = round((passed / total * 100), 2) if total > 0 else 0

    # Příprava dat pro grafy (omezíme historii např. na posledních 50 běhů pro přehlednost)
    chart_data = []
    for r in results[-50:]:
        chart_data.append({
            "name": r.get("test_name", "Neznámý test"),
            "duration": round(r.get("duration", 0), 2),
            "status": r.get("status", "unknown").capitalize(),
            "date": r.get("timestamp").strftime("%H:%M:%S") if r.get("timestamp") else ""
        })

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "passRate": pass_rate,
        "avgDuration": round(avg_duration, 2),
        "chartData": chart_data
    }