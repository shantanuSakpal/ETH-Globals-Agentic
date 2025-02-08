// app-sidebar-normal.tsx
"use client";

import {
  LayoutDashboard,
  MessageSquare,
  Bot,
  Zap,
  HelpCircle,
} from "lucide-react";
import Link from "next/link";
import { SidebarUserNav } from "@/components/sidebar-user-nav";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from "@/components/ui/sidebar";

const sidebarItems = [
  { icon: MessageSquare, label: "Chat", href: "/" },
  { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard" },
  { icon: Bot, label: "Manage Bots", href: "/manage-bots" },
];

export function AppSidebar({ user }: { user: any }) {
  // Using any to fix the immediate error
  return (
    <Sidebar className="bg-black ">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link href="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-white text-black">
                  <Zap className="size-5" />
                </div>
                <div className="flex flex-col  leading-none">
                  <span className="font-semibold text-lg">Helenus AI</span>
                  <span className="text-xs text-gray-400">v1.0.0</span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {sidebarItems.map((item) => (
                <SidebarMenuItem key={item.label}>
                  <SidebarMenuButton asChild>
                    <Link
                      href={item.href}
                      className="flex items-center gap-2 hover:bg-gray-800 p-2 rounded-md"
                    >
                      <item.icon className="size-4 text-gray-500" />
                      <span className="text-gray-500">{item.label}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel className="text-gray-400">
            Support
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link
                    href="/help"
                    className="flex items-center gap-2 hover:bg-gray-800 p-2 rounded-md"
                  >
                    <HelpCircle className="size-4 text-gray-500" />
                    <span className="text-gray-500">Help & Resources</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <div className="mb-3">
        <SidebarUserNav user={user} />
      </div>
    </Sidebar>
  );
}
