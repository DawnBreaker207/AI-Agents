import {getReportById} from "~/lib/ai.service";
import type {Route} from "./+types/report-detail";
import {Link} from "react-router";
import {Button} from "~/components/ui/button";
import ResearchReportCard from "~/components/ResearchReportCard";

export async function loader({params}: Route.LoaderArgs) {
    const report = await getReportById(
        params.id);
    if (!report) throw new Response("Not Found", {status: 404});
    return {report};
}

export default function ReportDetail({loaderData}: Route.ComponentProps) {
    const {report} = loaderData;

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-4">
                <Button variant="outline" asChild size="sm">
                    <Link to="/">← Quay lại Dashboard</Link>
                </Button>
                <h1 className="text-xl font-bold">Chi tiết báo cáo</h1>
            </div>
            <ResearchReportCard report={report}/>
        </div>
    );
}