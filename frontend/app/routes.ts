import {type RouteConfig, index, layout, route} from "@react-router/dev/routes";

export default [
    layout("components/layouts/DashboardLayout.tsx", [
        index("routes/_index.tsx"),
        route("feed", "routes/feed.tsx"),
        route("reports", "routes/reports.tsx"),
        route("reports/:id", "routes/report-detail.tsx"),
        route("research", "routes/research.tsx"),
        route("sources", "routes/sources.tsx"),
        route("dashboard", "routes/dashboard.tsx"),
    ]),
] satisfies RouteConfig;
