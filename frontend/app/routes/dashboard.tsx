import {ReportCard} from "~/components/ReportCard";
import type {Route} from "./+types/dashboard";
import {getReports} from "~/lib/ai.service";
import type {ResearchReport} from "~/types";
import {startResearch} from "~/lib/report.client";
import {useFetcher} from "react-router";
import {Input} from "~/components/ui/input";
import {Button} from "~/components/ui/button";
import {Spinner} from "~/components/ui/spinner";

export async function loader({request}: Route.LoaderArgs) {
    const reports: ResearchReport[] = await getReports();
    return {reports};

}

export async function action({request}: Route.ActionArgs) {
    const formData = await request.formData();
    const topic = formData.get("topic") as string;
    const newReport = await startResearch(topic);
    return {newReport};
}

export default function Dashboard({loaderData}: Route.ComponentProps) {
    const {reports} = loaderData;
    const fetcher = useFetcher();

    const isSearching = fetcher.state !== "idle";
    return (
        <div className="space-y-8">
            {/* Khu vực nhập liệu cho Agent */}
            <section className="bg-white p-6 rounded-xl shadow-sm border">
                <h2 className="text-lg font-semibold mb-4">Yêu cầu Agent nghiên cứu mới</h2>
                <fetcher.Form method="post" className="flex gap-2">
                    <Input
                        name="topic"
                        placeholder="Nhập chủ đề bạn muốn nghiên cứu (ví dụ: AI in Fintech 2024)..."
                        disabled={isSearching}
                        required
                    />
                    <Button type="submit" disabled={isSearching}>
                        {isSearching ? <><Spinner className="mr-2"/> Agent đang chạy...</> : "Bắt đầu"}
                    </Button>
                </fetcher.Form>
                {isSearching && (
                    <p className="text-sm text-amber-600 mt-2 animate-pulse">
                        💡 Agent đang truy cập internet và tổng hợp dữ liệu, việc này có thể mất 30-60 giây...
                    </p>
                )}
            </section>

            <section>
                <h2 className="text-xl font-bold mb-4">Lịch sử báo cáo</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {reports.map((report) => (
                        <ReportCard key={report.id} report={report}/>
                    ))}
                </div>
            </section>
        </div>
    );
}