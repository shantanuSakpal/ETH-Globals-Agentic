import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar-normal";
import { auth } from "../(auth)/auth";
import { cookies } from "next/headers";
import Script from "next/script";

export const experimental_ppr = true;

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [session, cookieStore] = await Promise.all([auth(), cookies()]);

  const isCollapsed = cookieStore.get("sidebar:state")?.value !== "true";

  return (
    <html lang="en">
      <head>{/* Add any head elements here */}</head>
      <body className="overflow-hidden">
        {" "}
        {/* Prevent overflow on body */}
        <Script
          src="https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js"
          strategy="beforeInteractive"
        />
        <SidebarProvider defaultOpen={!isCollapsed}>
          <div className="flex h-screen">
            <AppSidebar user={session?.user} />
            <main className="flex-1 overflow-hidden p-6">
              {" "}
              {/* Prevent overflow in main */}
              {children}
            </main>
          </div>
        </SidebarProvider>
      </body>
    </html>
  );
}
