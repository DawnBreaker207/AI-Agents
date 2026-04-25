import {type RouteConfig, index, layout, route} from "@react-router/dev/routes";

export default [
    layout("routes/dashboard.tsx", [
        index("routes/_index.tsx"),
        route("reports/:id", "routes/report-detail.tsx"),
        route("feed", "routes/feed.tsx"),
        route("reports", "routes/reports.tsx"),
        route("research", "routes/research.tsx"),
        route("sources", "routes/sources.tsx"),
    ]),
] satisfies RouteConfig;
