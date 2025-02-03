// app/api/price-conversion/route.ts

import { NextResponse } from "next/server";

export async function GET(request: Request) {
  // Parse query parameters from the request URL
  console.log("asdfasdf ", request.url);
  const { searchParams } = new URL(request.url);

  // Extract query parameters
  const amount = searchParams.get("amount");
  const id = searchParams.get("id");
  const symbol = searchParams.get("symbol");
  const time = searchParams.get("time");
  const convert = searchParams.get("convert");
  const convert_id = searchParams.get("convert_id");

  // Validate required parameters
  if (!amount || (!id && !symbol)) {
    return NextResponse.json(
      { error: "Amount and either id or symbol are required." },
      { status: 400 }
    );
  }

  // Build the query string for the API request
  const apiUrl = new URL(
    "https://pro-api.coinmarketcap.com/v2/tools/price-conversion"
  );
  apiUrl.searchParams.append("amount", amount);

  if (id) {
    apiUrl.searchParams.append("id", id);
  }

  if (symbol) {
    apiUrl.searchParams.append("symbol", symbol);
  }

  if (time) {
    apiUrl.searchParams.append("time", time);
  }

  if (convert) {
    apiUrl.searchParams.append("convert", convert);
  }

  if (convert_id) {
    apiUrl.searchParams.append("convert_id", convert_id);
  }

  // Fetch data from CoinMarketCap API
  console.log("post url -- ", apiUrl);
  try {
    const response = await fetch(apiUrl.toString(), {
      method: "GET",
      headers: {
        "X-CMC_PRO_API_KEY": process.env.NEXT_PUBLIC_CMC_API_KEY!, // Replace with your actual API key
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Error fetching data: ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
