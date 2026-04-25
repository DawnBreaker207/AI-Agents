import {useSearchParams} from "react-router-dom";
import {Input} from "~/components/ui/input";
import {Button} from "~/components/ui/button";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "~/components/ui/select";
import {Form} from "react-router";

export function ReportFilter() {
    const [searchParams] = useSearchParams();

    return (
        <Form method="get" className="flex flex-wrap items-center gap-4 p-4 bg-white rounded-lg shadow-sm mb-6">
            <div className="flex-1 min-w-50">
                <Input
                    type="search"
                    placeholder="Tìm kiếm theo tiêu đề..."
                    className="w-full"
                    defaultValue={searchParams.get("search") || ""}
                />
            </div>
            <div className="min-w-37.5">
                <Select name="category" defaultValue={searchParams.get("category") || ""}>
                    <SelectTrigger className="w-full">
                        <SelectValue placeholder="Chọn danh mục"/>
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">Tất cả danh mục</SelectItem>
                        <SelectItem value="technology">Công nghệ</SelectItem>
                        <SelectItem value="jobs">Công việc</SelectItem>
                        <SelectItem value="market">Thị trường</SelectItem>
                    </SelectContent>
                </Select>
            </div>
            <Button type="submit">Lọc báo cáo</Button>
        </Form>
    );
}