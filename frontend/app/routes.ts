import {type RouteConfig, index, layout, route} from "@react-router/dev/routes";

export default [
    layout("components/layouts/DashboardLayout.tsx", [
        index("routes/dashboard.tsx"),
        route("/reports/:id", "routes/report-detail.tsx")
    ]),
] satisfies RouteConfig;
