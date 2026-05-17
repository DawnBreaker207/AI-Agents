import type { Route } from "./+types/sources";
import { getSources, toggleSource, getWhitelist, addWhitelistTopic, deleteWhitelistTopic } from "~/lib/api";
import { Form, useNavigation, useActionData } from "react-router";
import {
  Table, TableBody, TableCell, TableHead,
  TableHeader, TableRow
} from "~/components/ui/table";
import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "~/components/ui/card";
import { Radio, Power, PowerOff, ShieldAlert, Plus, Trash2, Settings } from "lucide-react";
import { useRef, useEffect } from "react";

export async function loader({ request }: Route.LoaderArgs) {
  try {
    const [sources, whitelist] = await Promise.all([
      getSources(),
      getWhitelist()
    ]);
    return { sources, whitelist };
  } catch (err) {
    console.error("Sources loader failed, returning empty states:", err);
    return { sources: [], whitelist: [] };
  }
}

export async function action({ request }: Route.ActionArgs) {
  const formData = await request.formData();
  const intent = formData.get("intent") as string;

  if (intent === "toggle-source") {
    const sourceId = Number(formData.get("sourceId"));
    if (sourceId) {
      await toggleSource(sourceId);
    }
  } else if (intent === "add-whitelist") {
    const topic = formData.get("topic") as string;
    const boostScore = Number(formData.get("boost_score") || 1.5);
    const forceKeep = formData.get("force_keep") === "on"; // Checkbox is "on" when checked
    if (topic) {
      await addWhitelistTopic(topic, boostScore, forceKeep);
    }
  } else if (intent === "delete-whitelist") {
    const topicId = Number(formData.get("topicId"));
    if (topicId) {
      await deleteWhitelistTopic(topicId);
    }
  }

  return { success: true };
}

export default function SourcesPage({ loaderData }: Route.ComponentProps) {
  const { sources, whitelist } = loaderData;
  const navigation = useNavigation();
  const isSubmitting = navigation.state === "submitting";
  const submittingId = navigation.formData?.get("sourceId");
  const actionData = useActionData();

  const addFormRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (navigation.state === "idle" && actionData?.success) {
      addFormRef.current?.reset();
    }
  }, [navigation.state, actionData]);

  const activeSources = sources.filter(s => s.is_active);
  const inactiveSources = sources.filter(s => !s.is_active);

  const renderTable = (list: typeof sources, title: string, isActive: boolean) => (
    <div className="space-y-4">
      <h3 className="text-sm font-bold flex items-center gap-2 uppercase tracking-wider text-muted-foreground">
        {isActive ? (
          <Power size={14} className="text-green-500" />
        ) : (
          <PowerOff size={14} className="text-muted-foreground/60" />
        )}
        {title}
        <Badge variant="secondary" className="ml-2 font-mono">{list.length}</Badge>
      </h3>
      <div className="border rounded-xl overflow-hidden bg-card/40 backdrop-blur-sm">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/20">
              <TableHead className="w-16 text-center">Active</TableHead>
              <TableHead>Nguồn</TableHead>
              <TableHead className="hidden md:table-cell">URL</TableHead>
              <TableHead className="w-20">Loại</TableHead>
              <TableHead className="w-20 text-center">Trọng số</TableHead>
              <TableHead className="w-28 text-right">Thao tác</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {list.map(source => {
              const isThisSubmitting = isSubmitting && String(submittingId) === String(source.id);
              return (
                <TableRow key={source.id} className="group hover:bg-muted/10 transition-colors">
                  <TableCell>
                    <div className={`h-2 w-2 rounded-full mx-auto transition-colors ${
                      source.is_active ? 'bg-green-500 shadow-[0_0_6px_#22c55e]' : 'bg-muted-foreground/30'
                    }`} />
                  </TableCell>
                  <TableCell className="font-semibold text-xs">{source.name}</TableCell>
                  <TableCell className="hidden md:table-cell">
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-muted-foreground hover:text-primary hover:underline truncate max-w-[200px] block"
                    >
                      {source.url.replace(/^https?:\/\//, '')}
                    </a>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="text-[9px] font-mono uppercase px-1.5 py-0">
                      {source.type}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-center font-mono text-xs">
                    {source.priority_weight}
                  </TableCell>
                  <TableCell className="text-right">
                    <Form method="post">
                      <input type="hidden" name="intent" value="toggle-source" />
                      <input type="hidden" name="sourceId" value={source.id} />
                      <Button
                        type="submit"
                        variant={source.is_active ? "outline" : "default"}
                        size="sm"
                        disabled={isSubmitting}
                        className="text-[9px] font-black uppercase tracking-wider h-7 px-3.5"
                      >
                        {isThisSubmitting
                          ? "..."
                          : source.is_active ? "Tắt" : "Bật"
                        }
                      </Button>
                    </Form>
                  </TableCell>
                </TableRow>
              );
            })}
            {list.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground/60 py-8 text-xs italic">
                  Không có nguồn tin nào ở trạng thái này
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );

  return (
    <div className="space-y-10 animate-in fade-in duration-500 max-w-7xl mx-auto pb-16">
      {/* ── HEADER ── */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b pb-6 border-border/50">
        <div className="space-y-1">
          <h2 className="text-3xl font-black italic uppercase tracking-tight flex items-center gap-3">
            <div className="p-2 bg-primary rounded-lg shadow-xl shadow-primary/20">
              <Settings className="text-primary-foreground" size={22} />
            </div>
            System Control Center
          </h2>
          <p className="text-muted-foreground text-sm font-medium italic">
            Quản lý Whitelist Topics và các nguồn dữ liệu RSS/Scraping của AI Agent.
          </p>
        </div>
        <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground uppercase tracking-widest bg-muted/40 px-3 py-1.5 rounded-lg border">
          <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse shadow-[0_0_6px_#10b981]" />
          Control_Registry: OK
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* ── WHITELIST MANAGEMENT (2 COLUMNS) ── */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="border shadow-lg rounded-2xl overflow-hidden bg-card/60 backdrop-blur-sm">
            <CardHeader className="border-b bg-muted/20">
              <CardTitle className="text-sm font-black uppercase tracking-wider flex items-center gap-2 text-primary">
                <ShieldAlert size={16} /> AI Whitelist Topics
              </CardTitle>
              <CardDescription className="text-xs italic">
                Các từ khóa ưu tiên bắt buộc giữ lại (Force Keep) hoặc tăng điểm số (Boost Score) khi AI lọc tin.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              
              {/* Add Whitelist Topic Form */}
              <Form ref={addFormRef} method="post" className="flex flex-wrap gap-4 items-end bg-muted/10 p-4 rounded-xl border">
                <input type="hidden" name="intent" value="add-whitelist" />
                <div className="flex-1 min-w-[200px] space-y-1.5">
                  <label className="text-[9px] font-black uppercase tracking-wider text-muted-foreground block">Tên Topic / Từ khóa</label>
                  <Input name="topic" required placeholder="Ví dụ: ChatGPT, Nvidia, VinFast..." className="h-9 text-xs bg-background" />
                </div>
                <div className="w-24 space-y-1.5">
                  <label className="text-[9px] font-black uppercase tracking-wider text-muted-foreground block">Boost Score</label>
                  <Input name="boost_score" type="number" step="0.1" defaultValue="1.5" className="h-9 text-xs font-mono bg-background text-center" />
                </div>
                <div className="flex items-center gap-2 pb-2">
                  <input type="checkbox" id="force_keep" name="force_keep" defaultChecked className="rounded border-input text-primary focus:ring-primary h-4 w-4 bg-background cursor-pointer" />
                  <label htmlFor="force_keep" className="text-[10px] font-bold uppercase tracking-wider cursor-pointer select-none">Force Keep</label>
                </div>
                <Button type="submit" disabled={isSubmitting} size="sm" className="h-9 px-4 font-black text-xs uppercase tracking-wider gap-1">
                  <Plus size={14} /> Thêm
                </Button>
              </Form>

              {/* Whitelist Table */}
              <div className="border rounded-xl overflow-hidden bg-background">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-muted/10">
                      <TableHead>Topic Whitelist</TableHead>
                      <TableHead className="w-24 text-center">Boost Score</TableHead>
                      <TableHead className="w-28 text-center">Force Keep</TableHead>
                      <TableHead className="w-16 text-right"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {whitelist.map(topic => (
                      <TableRow key={topic.id} className="hover:bg-muted/5 transition-colors">
                        <TableCell className="font-bold text-xs">{topic.topic}</TableCell>
                        <TableCell className="text-center font-mono text-xs text-orange-500 font-semibold">
                          x{topic.boost_score}
                        </TableCell>
                        <TableCell className="text-center">
                          <Badge variant={topic.force_keep ? "default" : "outline"} className="text-[9px] font-black uppercase px-2 py-0">
                            {topic.force_keep ? "BẮT BUỘC" : "TÙY CHỌN"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Form method="post">
                            <input type="hidden" name="intent" value="delete-whitelist" />
                            <input type="hidden" name="topicId" value={topic.id} />
                            <Button
                              type="submit"
                              variant="ghost"
                              size="icon"
                              disabled={isSubmitting}
                              className="text-muted-foreground hover:text-destructive h-8 w-8 rounded-lg"
                            >
                              <Trash2 size={14} />
                            </Button>
                          </Form>
                        </TableCell>
                      </TableRow>
                    ))}
                    {whitelist.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={4} className="text-center text-muted-foreground/60 py-10 text-xs italic">
                          Chưa có từ khóa ưu tiên nào được cấu hình
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>

            </CardContent>
          </Card>
        </div>

        {/* ── RSS SOURCES (1 COLUMN) ── */}
        <div className="space-y-6">
          <Card className="border shadow-lg rounded-2xl overflow-hidden bg-card/60 backdrop-blur-sm h-full">
            <CardHeader className="border-b bg-muted/20">
              <CardTitle className="text-sm font-black uppercase tracking-wider flex items-center gap-2 text-primary">
                <Radio size={16} /> RSS & Scraping Sources
              </CardTitle>
              <CardDescription className="text-xs italic">
                Các đầu mối thu thập dữ liệu RSS hoạt động trong hệ thống.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6 space-y-8">
              {renderTable(activeSources, "Đang Bật", true)}
              {renderTable(inactiveSources, "Đang Tắt", false)}
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}