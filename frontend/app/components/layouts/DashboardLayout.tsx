import type {ReactNode} from "react";
import {NavLink, Outlet} from "react-router";
import {cn} from "~/lib/utils";


export function DashboardLayout({children}: { children: ReactNode }) {
    return (
        <div className="flex h-screen">
            <aside className="w-64 bg-gray-800 text-white p-4">
                <h2 className="text2xl font-bold mb-6">AI Agent Dashboard</h2>
                <nav className="space-y-2">
                    <NavLink to="/dashboard" end
                             className={({isActive}) => cn("block py-2 px-3 rounded-md hover:bg-gray-700", isActive && "bg-gray-700 font-semibold")}>
                        Báo Cáo
                    </NavLink>
                </nav>
            </aside>
            <main className="flex-1 p-6 bg-gray-100 overflow-y-auto">
                <div className="max-w-7xl mx-auto">
                    <Outlet/>
                </div>
            </main>
        </div>
    );
}