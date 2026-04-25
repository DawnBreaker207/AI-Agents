import type {Route} from "./+types/feed";
import {Clock, ExternalLink, Filter, Globe, Search, Sparkles} from "lucide-react";
import {Input} from "~/components/ui/input";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "~/components/ui/select";
import {Button} from "~/components/ui/button";
import {ScrollArea} from "~/components/ui/scroll-area";
import {Card, CardTitle} from "~/components/ui/card";
import {Badge} from "~/components/ui/badge";

export async function loader({request}: Route.LoaderArgs) {
    const newsItems = [
        {
            id: 1,
            title: "Nvidia thảo luận thiết lập trung tâm AI tại Việt Nam",
            summary: "Đại diện Nvidia đã có buổi làm việc với Chính phủ về việc xây dựng cơ sở hạ tầng bán dẫn...",
            source: "Reuters",
            url: "https://reuters.com",
            category: "Semiconductor",
            region: "Vietnam",
            sentiment: "Positive",
            timestamp: "10 phút trước",
            impactScore: 92
        },
        {
            id: 2,
            title: "Apple tăng cường tuyển dụng kỹ sư AI tại Đông Nam Á",
            summary: "Làn sóng dịch chuyển chuỗi cung ứng phần mềm đang đổ dồn vào khu vực...",
            source: "TechCrunch",
            url: "https://techcrunch.com",
            category: "Big Tech",
            region: "Global",
            sentiment: "Neutral",
            timestamp: "1 giờ trước",
            impactScore: 75
        },
        {
            id: 3,
            title: "Startup AI Việt Nam gọi vốn thành công 10 triệu USD",
            summary: "Một startup chuyên về LLM tiếng Việt vừa công bố vòng gọi vốn Series A...",
            source: "VnExpress",
            url: "https://vnexpress.net",
            category: "Startup",
            region: "Vietnam",
            sentiment: "Positive",
            timestamp: "3 giờ trước",
            impactScore: 85
        }
    ];
    return {newsItems};
}


export default function MarketFeed({loaderData}: Route.ComponentProps) {
    const {newsItems} = loaderData;

    return (
        <div className="flex flex-col h-[calc(100vh-120px)] space-y-4">
            {/* HEADER TRANG FEED */}
            <div
                className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-4 rounded-xl border shadow-sm">
                <div>
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <Globe className="text-blue-600" size={24}/>
                        Live Market Feed
                    </h2>
                    <p className="text-sm text-muted-foreground">Luồng tin tức IT thời gian thực từ 50+ nguồn uy
                        tín.</p>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                    <div className="relative w-64">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground"/>
                        <Input placeholder="Lọc tin tức..." className="pl-8 h-9"/>
                    </div>
                    <Select defaultValue="all">
                        <SelectTrigger className="w-[130px] h-9">
                            <SelectValue placeholder="Khu vực"/>
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">Toàn thế giới</SelectItem>
                            <SelectItem value="vn">Việt Nam</SelectItem>
                            <SelectItem value="global">Quốc tế</SelectItem>
                        </SelectContent>
                    </Select>
                    <Button variant="outline" size="sm" className="h-9">
                        <Filter size={14} className="mr-2"/> Filters
                    </Button>
                </div>
            </div>

            {/* DANH SÁCH TIN TỨC */}
            <ScrollArea className="flex-1 pr-4">
                <div className="grid gap-4">
                    {newsItems.map((item) => (
                        <Card key={item.id}
                              className="group hover:border-blue-300 transition-all shadow-sm overflow-hidden">
                            <div className="flex flex-col md:flex-row">
                                {/* IMPACT SCORE SIDEBAR */}
                                <div className={`w-1.5 ${item.impactScore > 80 ? 'bg-red-500' : 'bg-blue-500'}`}/>

                                <div className="flex-1 p-5">
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex flex-wrap gap-2 items-center text-xs font-medium">
                                            <Badge variant="outline" className="bg-slate-50">{item.source}</Badge>
                                            <span className="text-muted-foreground flex items-center gap-1">
                        <Clock size={12}/> {item.timestamp}
                      </span>
                                            <Badge className={
                                                item.sentiment === 'Positive' ? 'bg-green-50 text-green-700 border-green-200' :
                                                    'bg-slate-50 text-slate-700 border-slate-200'
                                            }>
                                                {item.sentiment}
                                            </Badge>
                                        </div>
                                        <div className="flex items-center gap-1 text-xs font-bold text-blue-600">
                                            Impact: {item.impactScore}
                                        </div>
                                    </div>

                                    <CardTitle className="text-xl mb-2 group-hover:text-blue-600 transition-colors">
                                        {item.title}
                                    </CardTitle>

                                    <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
                                        {item.summary}
                                    </p>

                                    <div className="flex justify-between items-center">
                                        <div className="flex gap-2">
                                            <Badge variant="secondary"
                                                   className="text-[10px] tracking-wider uppercase">{item.category}</Badge>
                                            <Badge variant="secondary"
                                                   className="text-[10px] tracking-wider uppercase">{item.region}</Badge>
                                        </div>

                                        <div className="flex items-center gap-2">
                                            <Button variant="ghost" size="sm" className="text-xs gap-1">
                                                <Sparkles size={14} className="text-amber-500"/> Phân tích sâu
                                            </Button>
                                            <Button variant="link" size="sm" className="text-xs gap-1 h-auto p-0"
                                                    asChild>
                                                <a href={item.url} target="_blank" rel="noreferrer">
                                                    Nguồn gốc <ExternalLink size={12}/>
                                                </a>
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            </ScrollArea>
        </div>
    )
}