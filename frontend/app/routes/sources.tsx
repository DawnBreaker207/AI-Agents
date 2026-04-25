import {Button} from "~/components/ui/button";
import {Globe, Plus, Rss} from "lucide-react";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "~/components/ui/table";
import {Badge} from "~/components/ui/badge";
import {Switch} from "~/components/ui/switch";
import type {Route} from "./+types/research";

const sources = [
    {name: "VnExpress International", type: "Web", url: "vnexpress.net", status: true, lastScan: "20 phút trước"},
    {name: "TechCrunch - AI Section", type: "RSS", url: "techcrunch.com", status: true, lastScan: "1 giờ trước"},
    {name: "IT Jobs Vietnam LinkedIn", type: "Social", url: "linkedin.com", status: false, lastScan: "3 ngày trước"},
];

export async function action({request}: Route.ActionArgs) {
    const formData = await request.formData();
    const prompt = formData.get("prompt") as string;
    return {success: true};
}

export default function SourcesPage() {
    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold">Knowledge Sources</h2>
                    <p className="text-muted-foreground">Quản lý danh sách các nguồn tin Agent sẽ cào dữ liệu.</p>
                </div>
                <Button className="gap-2">
                    <Plus size={16}/> Add New Source
                </Button>
            </div>

            <div className="border rounded-xl bg-white shadow-sm overflow-hidden">
                <Table>
                    <TableHeader className="bg-muted/50">
                        <TableRow>
                            <TableHead className="w-[300px]">Source Name</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Last Scanned</TableHead>
                            <TableHead className="text-right">Action</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {sources.map((source) => (
                            <TableRow key={source.name}>
                                <TableCell className="font-medium">
                                    <div className="flex flex-col">
                                        <span>{source.name}</span>
                                        <span className="text-xs text-muted-foreground">{source.url}</span>
                                    </div>
                                </TableCell>
                                <TableCell>
                                    <Badge variant="outline" className="gap-1 font-normal">
                                        {source.type === "Web" && <Globe size={12}/>}
                                        {source.type === "RSS" && <Rss size={12}/>}
                                        {source.type === "Social" && <Rss size={12}/>}
                                        {source.type}
                                    </Badge>
                                </TableCell>
                                <TableCell>
                                    <Switch checked={source.status}/>
                                </TableCell>
                                <TableCell className="text-sm text-muted-foreground">
                                    {source.lastScan}
                                </TableCell>
                                <TableCell className="text-right">
                                    <Button variant="ghost" size="sm">Edit</Button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    )
}