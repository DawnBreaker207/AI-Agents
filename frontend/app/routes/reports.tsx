import {Button} from "~/components/ui/button";
import {Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle} from "~/components/ui/card";
import {Badge} from "~/components/ui/badge";
import {Calendar, Download, Eye} from "lucide-react";
import type {Route} from "./+types/reports";

const reports = [
    {
        id: 1,
        title: "Báo cáo thị trường Semiconductor Việt Nam Q2/2024",
        description: "Phân tích làn sóng đầu tư từ Nvidia, Samsung và cơ hội cho nhân lực nội địa.",
        date: "20/05/2024",
        category: "Deep Dive",
        status: "New"
    },
    {
        id: 2,
        title: "Xu hướng tuyển dụng AI Engineer Toàn cầu",
        description: "Tổng hợp các kỹ năng đang được săn đón nhất: RAG, Fine-tuning, LLMOps.",
        date: "18/05/2024",
        category: "Weekly Digest",
        status: "Read"
    }
];

export async function action({request}: Route.ActionArgs) {
    const formData = await request.formData();
    const prompt = formData.get("prompt") as string;
    return {success: true};
}

export default function ReportsPage() {
    return (
        <div className="space-y-6">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Insight Reports</h2>
                    <p className="text-muted-foreground">Báo cáo chiến lược được tổng hợp bởi Agentic AI.</p>
                </div>
                <Button variant="outline">Tải tất cả báo cáo (.PDF)</Button>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {reports.map((report) => (
                    <Card key={report.id} className="flex flex-col">
                        <CardHeader>
                            <div className="flex justify-between items-start mb-2">
                                <Badge variant={report.category === "Deep Dive" ? "default" : "secondary"}>
                                    {report.category}
                                </Badge>
                                {report.status === "New" &&
                                    <span className="flex h-2 w-2 rounded-full bg-blue-500"></span>}
                            </div>
                            <CardTitle className="leading-tight">{report.title}</CardTitle>
                            <CardDescription className="pt-2">{report.description}</CardDescription>
                        </CardHeader>
                        <CardContent className="flex-1">
                            <div className="flex items-center text-sm text-muted-foreground gap-2">
                                <Calendar size={14}/> {report.date}
                            </div>
                        </CardContent>
                        <CardFooter className="border-t pt-4 flex justify-between">
                            <Button variant="ghost" size="sm" className="gap-2">
                                <Eye size={14}/> Xem chi tiết
                            </Button>
                            <Button variant="ghost" size="sm" className="gap-2">
                                <Download size={14}/> PDF
                            </Button>
                        </CardFooter>
                    </Card>
                ))}
            </div>
        </div>
    )
}