"use client"

import { LayoutDashboard, MessageSquare, Bot, Settings, Users, Zap, HelpCircle } from "lucide-react"
import Link from "next/link"
import { SidebarUserNav } from "@/components/sidebar-user-nav"
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
} from "@/components/ui/sidebar"

// Define the expected user type
interface User {
  name: string;
  email: string;
  avatarUrl?: string;
}

const sidebarItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard" },
  { icon: MessageSquare, label: "Chat", href: "/chat" },
  { icon: Bot, label: "Manage Bots", href: "/manage-bots" },
//   { icon: Users, label: "Team", href: "/team" },
//   { icon: Zap, label: "Integrations", href: "/integrations" },
//   { icon: Settings, label: "Settings", href: "/settings" },
]

// Accept a user prop in AppSidebar
export function AppSidebar({ user }: { user: User }) {
   
  return (
    <Sidebar className="bg-black text-white">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link href="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-white text-black">
                  <Zap className="size-5" />
                </div>
                <div className="flex flex-col gap-0.5 leading-none">
                  <span className="font-semibold">Helenus AI</span>
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
                    <Link href={item.href} className="flex items-center gap-2 hover:bg-gray-800 p-2 rounded-md">
                      <item.icon className="size-4 text-gray-300" />
                      <span className="text-gray-200">{item.label}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel className="text-gray-400">Support</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/help" className="flex items-center gap-2 hover:bg-gray-800 p-2 rounded-md">
                    <HelpCircle className="size-4 text-gray-300" />
                    <span className="text-gray-200">Help & Resources</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      {/* Pass user prop to SidebarUserNav */}
      <div className="mb-3">
      <SidebarUserNav user={user} />
      </div>
    </Sidebar>
  )
}
