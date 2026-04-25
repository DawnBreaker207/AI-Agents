import {useFetcher} from "react-router";
import {Input} from "~/components/ui/input";
import {Button} from "~/components/ui/button";
import {Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle} from "~/components/ui/card";
import {Activity, Clock, Cpu, FileText, Loader2, Newspaper, Search, TrendingUp, Zap} from "lucide-react";
import {Badge} from "~/components/ui/badge";

export async function loader() {
    return {
        reports: [
            {
                id: 1,
                title: "Phân tích xu hướng AI trong ngành Fintech Việt Nam 2024",
                createdAt: "2 giờ trước",
                sourcesCount: 12,
                type: "Phân tích"
            },
            {
                id: 2,
                title: "Báo cáo thị trường bán dẫn (Semiconductor) Đông Nam Á",
                createdAt: "1 ngày trước",
                sourcesCount: 25,
                type: "Thị trường"
            },
            {
                id: 3,
                title: "Làn sóng sa thải ngành IT toàn cầu và tác động tới VN",
                createdAt: "3 ngày trước",
                sourcesCount: 18,
                type: "Nhân sự"
            },
        ],
        stats: {
            totalScanned: 1542,
            activeAgents: 4,
            systemHealth: "Good"
        }
    };

}

export async function action() {
    await new Promise((resolve) => setTimeout(resolve, 2000)); // Chờ 2s giả lập
    return {success: true};
}

export default function Dashboard({loaderData}: { loaderData: any }) {
    const {reports, stats} = loaderData;
    const fetcher = useFetcher();
    const isSearching = fetcher.state !== "idle";
    return (
        <div className="space-y-6">
            {/* HÀNG 1: CHỈ SỐ KPI GIẢ LẬP */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card className="bg-[#0f172a] text-white border-none shadow-lg">
                    <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
                        <CardTitle className="text-xs font-bold uppercase opacity-60 tracking-wider">Tin tức đã
                            quét</CardTitle>
                        <Newspaper size={16} className="opacity-60"/>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{stats.totalScanned}</div>
                        <p className="text-[10px] text-blue-400 mt-1 font-medium">+124 tin mới sáng nay</p>
                    </CardContent>
                </Card>

                <Card className="shadow-sm border-slate-200">
                    <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
                        <CardTitle className="text-xs font-bold uppercase text-slate-500 tracking-wider">Báo cáo sẵn
                            sàng</CardTitle>
                        <FileText size={16} className="text-blue-600"/>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{reports.length}</div>
                        <p className="text-[10px] text-green-600 mt-1 flex items-center gap-1 font-bold">
                            <TrendingUp size={10}/> Ổn định
                        </p>
                    </CardContent>
                </Card>

                <Card className="shadow-sm border-slate-200">
                    <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
                        <CardTitle className="text-xs font-bold uppercase text-slate-500 tracking-wider">Hệ thống
                            Agent</CardTitle>
                        <Cpu size={16} className="text-blue-600"/>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{stats.activeAgents} Online</div>
                        <div className="flex items-center gap-1.5 mt-1.5">
                            <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse"/>
                            <span className="text-[10px] font-bold text-slate-500">Status: {stats.systemHealth}</span>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* HÀNG 2: FORM NHẬP NGHIÊN CỨU (Logic fetcher của bạn) */}
            <Card className="border-blue-100 shadow-md">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-xl">
                        <Zap className="text-blue-600" fill="currentColor" size={20}/>
                        Yêu cầu Agent nghiên cứu mới
                    </CardTitle>
                    <CardDescription>
                        Nhập chủ đề công nghệ bạn muốn tìm hiểu. Agent sẽ quét Google, LinkedIn và TechCrunch.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <fetcher.Form method="post" className="flex gap-2">
                        <Input
                            name="topic"
                            placeholder="Ví dụ: Tình hình nhân sự IT tại Đà Nẵng 2024..."
                            disabled={isSearching}
                            required
                            className="flex-1 h-12 text-base focus-visible:ring-blue-500"
                        />
                        <Button type="submit" disabled={isSearching}
                                className="h-12 px-10 bg-blue-600 hover:bg-blue-700 font-bold transition-all">
                            {isSearching ? <Loader2 className="animate-spin mr-2" size={20}/> :
                                <Search size={20} className="mr-2"/>}
                            {isSearching ? "Đang xử lý..." : "Bắt đầu"}
                        </Button>
                    </fetcher.Form>

                    {/* Hiệu ứng giả lập AI đang chạy */}
                    {isSearching && (
                        <div className="mt-6 p-5 rounded-xl bg-slate-50 border border-dashed border-blue-200 space-y-3">
                            <div className="flex items-center gap-3 text-sm text-blue-700 font-bold animate-pulse">
                                <Activity size={18}/>
                                <span>Agent đang kết nối Internet và thu thập dữ liệu nguồn...</span>
                            </div>
                            <div className="flex gap-2">
                                <Badge variant="outline" className="bg-white animate-bounce">Đang đọc VnExpress</Badge>
                                <Badge variant="outline" className="bg-white animate-bounce [animation-delay:0.2s]">Truy
                                    vấn LinkedIn</Badge>
                                <Badge variant="outline" className="bg-white animate-bounce [animation-delay:0.4s]">Tổng
                                    hợp dữ liệu</Badge>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* HÀNG 3: LỊCH SỬ BÁO CÁO GIẢ LẬP */}
            <div className="space-y-4 pt-4">
                <div className="flex justify-between items-center">
                    <h2 className="text-xl font-bold tracking-tight flex items-center gap-2">
                        <Clock className="text-slate-400" size={20}/> Báo cáo gần đây
                    </h2>
                    <Button variant="link" className="text-blue-600 font-bold">Xem tất cả báo cáo →</Button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {reports.map((report: any) => (
                        <Card key={report.id}
                              className="group hover:border-blue-400 transition-all cursor-pointer shadow-sm">
                            <CardHeader className="p-5 pb-3">
                                <div className="flex justify-between items-start mb-3">
                                    <Badge
                                        className="bg-blue-50 text-blue-700 hover:bg-blue-50 border-none text-[10px] font-bold uppercase tracking-wider">
                                        {report.type}
                                    </Badge>
                                    <span
                                        className="text-[10px] font-medium text-slate-400 uppercase tracking-tighter">{report.createdAt}</span>
                                </div>
                                <CardTitle
                                    className="text-md font-bold leading-tight group-hover:text-blue-600 transition-colors">
                                    {report.title}
                                </CardTitle>
                            </CardHeader>
                            <CardFooter
                                className="p-5 pt-0 flex justify-between items-center border-t border-slate-50 mt-4">
                                <div className="text-[11px] font-medium text-slate-500">
                                    {report.sourcesCount} nguồn dẫn chứng
                                </div>
                                <Button variant="ghost" size="sm"
                                        className="h-8 text-xs font-bold text-blue-600 p-0 hover:bg-transparent">
                                    Xem chi tiết <TrendingUp size={12} className="ml-1"/>
                                </Button>
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    );
}