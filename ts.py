import sys
import os

# fix module path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from ml_engine.pipelines.region_trend_pipeline import RegionTrendPipeline


def main():

    pipeline = RegionTrendPipeline()

    texts = [
        "Heavy rain in Chennai causing floods",
        "Flood alert in Coimbatore",
        "IPL match in Mumbai",
        "Traffic jam in Bangalore",
        "Rain again in Chennai streets"
    ]

    result = pipeline.run(texts, target_state="tamil nadu")

    print("\n🔥 FINAL RESULT:\n")
    for r in result:
        print(r)


if __name__ == "__main__":
    main()