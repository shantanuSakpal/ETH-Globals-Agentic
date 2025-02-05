// utils/getCoinPrice.ts

export default async function getCoinPrice(
  amount: number,
  id?: string,
  symbol?: string,
  time?: string,
  convert?: string,
  convert_id?: string
) {
  console.log("funnidn get coin");

  // Base URL for CoinMarketCap API price conversion
  const apiUrl = "https://pro-api.coinmarketcap.com/v2/tools/price-conversion";

  // Prepare the query parameters
  const params = new URLSearchParams();
  params.append("amount", amount.toString());

  if (id) {
    params.append("id", id);
  }

  if (symbol) {
    params.append("symbol", symbol);
  }

  if (time) {
    params.append("time", time);
  }

  if (convert) {
    params.append("convert", convert);
  }

  if (convert_id) {
    params.append("convert_id", convert_id);
  }

  // Append the query parameters to the API URL
  const urlWithParams = `${apiUrl}?${params.toString()}`;
  console.log("url ", urlWithParams);

  try {
    const response = await fetch(urlWithParams, {
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
    console.log(data); // Log the fetched data
    return data; // Return the fetched data for further use
  } catch (error: any) {
    console.error("Error:", error.message); // Log any errors
    throw error; // Rethrow the error for handling in calling code
  }
}
