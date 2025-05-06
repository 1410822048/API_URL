import asyncio
import discord
import os
from discord.ext import commands, tasks
from playwright.async_api import async_playwright
from datetime import datetime, timedelta, timezone
import time


# 你的 Discord bot token
TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("請設置環境變數 DISCORD_TOKEN！")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

intents = discord.Intents.default()
intents.message_content = True  # 啟用 Message Content Intent
bot = commands.Bot(command_prefix="!", intents=intents)

# 設定 Discord bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)


# 假設你有一堆 API url
api_urls = [
    "https://aic-api-management.azure-api.net/HIS/GetExamReport",
    "https://aic-api-management.azure-api.net/HIS/GetEmgNsRecord",
    "https://aic-api-management.azure-api.net/HIS/GetEmgNsPractice",
    "https://aic-api-management.azure-api.net/HIS/GetNursingRecord",
    "https://aic-api-management.azure-api.net/HIS/GetAdmissionNote",
    "https://aic-api-management.azure-api.net/HIS/GetProgressNoteSummary",
    "https://aic-api-management.azure-api.net/HIS/GetUsingMedDrug",
    "https://aic-api-management.azure-api.net/HIS/GetLabReportValueBy2010",
    "https://aic-api-management.azure-api.net/HIS/GetLabReportValueBy2030",
    "https://aic-api-management.azure-api.net/HIS/GetMedDrug",
    "https://aic-api-management.azure-api.net/HIS/GetEmgNote",
    "https://aic-api-management.azure-api.net/HIS/GetLabReportValueBy2110",
    "https://aic-api-management.azure-api.net/HIS/GetFormatedTPRRecord",
    "https://aic-api-management.azure-api.net/HIS/GetNursePlanCause",
    "https://aic-api-management.azure-api.net/HIS/GetNursePlan",
    "https://aic-api-management.azure-api.net/HIS/GetNursePlanCharact",
    "https://aic-api-management.azure-api.net/HIS/GetNursePlanSubjective",
    "https://aic-api-management.azure-api.net/HIS/GetNursePlanGoal",
    "https://aic-api-management.azure-api.net/HIS/GetNursePlanIntervention",
    "https://aic-api-management.azure-api.net/HIS/GetInfectDrugCheck",
    "https://aic-api-management.azure-api.net/HIS/GetLabReportText",
    "https://aic-api-management.azure-api.net/HIS/GetOperBodyIdAllData",
    "https://aic-api-management.azure-api.net/HIS/GetSOP",
    "https://aic-api-management.azure-api.net/HIS/GetAssessment",
    "https://aic-api-management.azure-api.net/HIS/GetMedAllergy",
    "https://aic-api-management.azure-api.net/HIS/GetNhiCloudQuery",
    "https://aic-api-management.azure-api.net/HIS/GetMedHistory",
    "https://aic-api-management.azure-api.net/HIS/GetPcTestRecord",
    "https://aic-api-management.azure-api.net/HIS/GetNERecordForAdmission",
    "https://aic-api-management.azure-api.net/HIS/GetLabReportValue",
    "https://aic-api-management.azure-api.net/HIS/GetOperRecordData",
    "https://aic-api-management.azure-api.net/HIS/GetIcuMeasureRecord",
    "https://aic-api-management.azure-api.net/HIS/GetChemoDrug",
    "https://aic-api-management.azure-api.net/HIS/GetDischargeNote",
    "https://aic-api-management.azure-api.net/HIS/GetDiagRecord",
    "https://aic-api-management.azure-api.net/HIS/GetExamRecord",
    "https://aic-api-management.azure-api.net/HIS/GetInpVisitRecord",
    "https://aic-api-management.azure-api.net/HIS/GetEmgVisitRecord",
    "https://aic-api-management.azure-api.net/HIS/GetOpdVisitRecord",
    "https://aic-api-management.azure-api.net/HIS/GetChemoInfo",
    "https://aic-api-management.azure-api.net/HIS/GetFirstVisitChart",
    "https://aic-api-management.azure-api.net/HIS/GetTPRRecord",
    "https://aic-api-management.azure-api.net/HIS/GetPostOperNsAssessList",
    "https://aic-api-management.azure-api.net/HIS/GetInpNurTransShiftByExam",
    "https://aic-api-management.azure-api.net/HIS/GetOperSchedulAllData",
    "https://aic-api-management.azure-api.net/HIS/GetOperSchedulData",
    "https://aic-api-management.azure-api.net/HIS/GetOperSchedulImage",
    "https://aic-api-management.azure-api.net/HIS/GetOperBodyIdAllData",
    "https://aic-api-management.azure-api.net/HIS/GetOperBodyIdData",
    "https://aic-api-management.azure-api.net/HIS/GetOperBodyIdImage",
]

# 要送出的資料
payload = {
    "ChartNo": "99999987",
    "Time": {"StartDate": "2025-02-27", "EndDate": "2025-03-27"},
}

# 錯誤 API 會記在這裡
error_apis = []


# API 測試函數
async def test_multiple_apis():
    total_apis = len(api_urls)  # 總測試 API 數量
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        for url in api_urls:
            try:
                response = await page.request.post(
                    url=url, data=payload, headers={"Content-Type": "application/json"}
                )

                status = response.status  # 取得狀態碼

                if status >= 400:
                    print(f"❌ 錯誤：{url} 回傳狀態碼 {status}")
                    error_apis.append({"url": url, "statusCode": status})
                else:
                    print(f"✅ 成功：{url} - 狀態碼 {status}")

            except Exception as e:
                print(f"🚨 例外錯誤：{url} - {e}")
                error_apis.append({"url": url, "statusCode": "exception"})

        await browser.close()

    # 測試結束後列出錯誤清單
    channel = bot.get_channel(int(CHANNEL_ID))
    if error_apis:
        msg = "\n🔴 有錯誤的 API：\n"
        for err in error_apis:
            short_url = err["url"].split("/")[-1]
            msg += f"{short_url} -> 狀態碼: {err['statusCode']}\n"
    else:
        msg = f"\n✅ 所有 {total_apis} 個 API 都通過測試！"
        print("\n✅ 所有 API 都通過測試！")
    await channel.send(msg)


@bot.event
async def on_ready():
    print("開始執行 API 測試...")
    await test_multiple_apis()
    print("測試完成，即將關閉 bot。")
    await bot.close()  # 登出機器人


# 啟動機器人
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"機器人啟動失敗: {e}")
