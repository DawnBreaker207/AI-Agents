import type { Route } from "./+types/sources";
import { getSources, toggleSource, getWhitelist, addWhitelistTopic, deleteWhitelistTopic, getAliases, addAlias, deleteAlias } from "~/lib/api";
import { Form, useNavigation, useActionData } from "react-router";
import {
  Table, TableBody, TableCell, TableHead,
  TableHeader, TableRow
} from "~/components/ui/table";
import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "~/components/ui/card";
import { Radio, Power, PowerOff, ShieldAlert, Plus, Trash2, Settings, Circle, Briefcase } from "lucide-react";
import { useRef, useEffect } from "react";

export async function loader({ request }: Route.LoaderArgs) {
  try {
    const [sources, whitelist, aliases] = await Promise.all([
      getSources(),
      getWhitelist(),
      getAliases()
    ]);
    return { sources, whitelist, aliases };
  } catch (err) {
    console.error("Sources loader failed, returning empty states:", err);
    return { sources: [], whitelist: [], aliases: [] };
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
  } else if (intent === "add-alias") {
    const canonical_role = formData.get("canonical_role") as string;
    const alias = formData.get("alias") as string;
    if (canonical_role && alias) {
      await addAlias(canonical_role, alias);
    }
  } else if (intent === "delete-alias") {
    const aliasId = Number(formData.get("aliasId"));
    if (aliasId) {
      await deleteAlias(aliasId);
    }
  }

  return { success: true };
}

export default function SourcesPage({ loaderData }: Route.ComponentProps) {
  const { sources, whitelist, aliases } = loaderData;
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
      <h3 className="text-[13px] font-medium flex items-center gap-2 text-muted-foreground">
        {isActive ? (
          <Power className="w-3.5 h-3.5 text-green-500" />
        ) : (
          <PowerOff className="w-3.5 h-3.5 text-muted-foreground/60" />
        )}
        {title}
        <span className="text-[11px] text-muted-foreground/60 ml-auto tabular-nums">{list.length}</span>
      </h3>
      <div className="border rounded-xl overflow-hidden bg-card/40">
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
                <TableRow key={source.id} className="group hover:bg-muted/10 motion-safe:transition-colors">
                  <TableCell>
                    <div className={`h-2 w-2 rounded-full mx-auto transition-colors ${
                      source.is_active ? 'bg-green-500' : 'bg-muted-foreground/30'
                    }`} />
                  </TableCell>
                  <TableCell className="font-medium text-xs">
                    <span className="flex items-center gap-2">
                      <Circle className={`w-2 h-2 fill-current ${source.type === "RSS" ? "text-green-500" : "text-blue-500"}`} />
                      {source.name}
                    </span>
                  </TableCell>
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
                        className="text-[9px] font-medium uppercase tracking-wider min-h-11 px-4"
                        aria-label={source.is_active ? `Tắt nguồn ${source.name}` : `Bật nguồn ${source.name}`}
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
    <div className="space-y-10 motion-safe:animate-in motion-safe:fade-in motion-safe:duration-500 max-w-7xl mx-auto pb-16">
      {/* ── HEADER ── */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b pb-6 border-border/50">
        <div className="space-y-1">
          <h1 className="text-lg font-medium text-foreground tracking-tight flex items-center gap-2">
            <Settings className="w-4 h-4 text-muted-foreground" />
            Quản lý nguồn tin
          </h1>
          <p className="text-[12px] text-muted-foreground">
            Quản lý whitelist topics và các nguồn dữ liệu RSS.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* ── WHITELIST MANAGEMENT (2 COLUMNS) ── */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="border border-border/50 rounded-xl overflow-hidden">
            <CardHeader className="border-b border-border/50">
              <CardTitle className="text-[13px] font-medium tracking-tight flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-muted-foreground" /> AI Whitelist Topics
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
                  <label htmlFor="topic-name" className="text-[9px] font-medium uppercase tracking-wider text-muted-foreground block">Tên Topic / Từ khóa</label>
                  <Input id="topic-name" name="topic" required placeholder="Ví dụ: ChatGPT, Nvidia, VinFast..." className="min-h-11 text-xs bg-background" />
                </div>
                <div className="w-24 space-y-1.5">
                  <label className="text-[9px] font-medium uppercase tracking-wider text-muted-foreground block">Boost Score</label>
                  <Input name="boost_score" type="number" step="0.1" defaultValue="1.5" className="h-9 text-xs font-mono bg-background text-center" />
                </div>
                <div className="flex items-center gap-2 pb-2">
                  <input type="checkbox" id="force_keep" name="force_keep" defaultChecked className="rounded border-input text-primary focus:ring-primary h-4 w-4 bg-background cursor-pointer" />
                  <label htmlFor="force_keep" className="text-[10px] font-medium uppercase tracking-wider cursor-pointer select-none">Force Keep</label>
                </div>
                <Button type="submit" disabled={isSubmitting} size="sm" className="h-9 px-4 font-medium text-xs uppercase tracking-wider gap-1">
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
                      <TableRow key={topic.id} className="hover:bg-muted/5 motion-safe:transition-colors">
                        <TableCell className="font-medium text-xs">{topic.topic}</TableCell>
                        <TableCell className="text-center font-mono text-xs text-amber-600 dark:text-amber-400 font-medium">
                          x{topic.boost_score}
                        </TableCell>
                        <TableCell className="text-center">
                          <Badge variant={topic.force_keep ? "default" : "outline"} className="text-[9px] font-medium uppercase px-2 py-0">
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
                              className="text-muted-foreground hover:text-destructive min-h-11 min-w-11 rounded-lg"
                              aria-label={`Xóa topic ${topic.topic}`}
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

          {/* ── ROLE ALIAS (4.2): từ điển đồng nghĩa vai trò cho Job Search ── */}
          <Card className="border border-border/50 rounded-xl overflow-hidden">
            <CardHeader className="border-b border-border/50">
              <CardTitle className="text-[13px] font-medium tracking-tight flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-muted-foreground" /> Role Alias — Job Search
              </CardTitle>
              <CardDescription className="text-xs italic">
                Tên gọi tương đương của cùng 1 vị trí (VD: Backend Developer ↔ Server-side Engineer).
                Tìm kiếm sẽ tự mở rộng theo alias.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <Form method="post" className="flex flex-wrap gap-4 items-end bg-muted/10 p-4 rounded-xl border">
                <input type="hidden" name="intent" value="add-alias" />
                <div className="flex-1 min-w-[160px] space-y-1.5">
                  <label htmlFor="canonical-role" className="text-[9px] font-medium uppercase tracking-wider text-muted-foreground block">Vai trò chuẩn</label>
                  <Input id="canonical-role" name="canonical_role" required placeholder="Ví dụ: Backend Developer" className="min-h-11 text-xs bg-background" />
                </div>
                <div className="flex-1 min-w-[160px] space-y-1.5">
                  <label htmlFor="alias-name" className="text-[9px] font-medium uppercase tracking-wider text-muted-foreground block">Tên tương đương (alias)</label>
                  <Input id="alias-name" name="alias" required placeholder="Ví dụ: Server-side Engineer" className="min-h-11 text-xs bg-background" />
                </div>
                <Button type="submit" disabled={isSubmitting} size="sm" className="h-9 px-4 font-medium text-xs uppercase tracking-wider gap-1">
                  <Plus size={14} /> Thêm
                </Button>
              </Form>

              <div className="border rounded-xl overflow-hidden bg-background">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-muted/10">
                      <TableHead>Vai trò chuẩn</TableHead>
                      <TableHead>Alias</TableHead>
                      <TableHead className="w-16 text-right"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {aliases.map(a => (
                      <TableRow key={a.id} className="hover:bg-muted/5 motion-safe:transition-colors">
                        <TableCell className="font-medium text-xs">{a.canonical_role}</TableCell>
                        <TableCell className="text-xs text-muted-foreground">{a.alias}</TableCell>
                        <TableCell className="text-right">
                          <Form method="post">
                            <input type="hidden" name="intent" value="delete-alias" />
                            <input type="hidden" name="aliasId" value={a.id} />
                            <Button
                              type="submit"
                              variant="ghost"
                              size="icon"
                              disabled={isSubmitting}
                              className="text-muted-foreground hover:text-destructive min-h-11 min-w-11 rounded-lg"
                              aria-label={`Xóa alias ${a.alias}`}
                            >
                              <Trash2 size={14} />
                            </Button>
                          </Form>
                        </TableCell>
                      </TableRow>
                    ))}
                    {aliases.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={3} className="text-center text-muted-foreground/60 py-10 text-xs italic">
                          Chưa có alias nào được cấu hình
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
          <Card className="border border-border/50 rounded-xl overflow-hidden h-full">
            <CardHeader className="border-b border-border/50">
              <CardTitle className="text-[13px] font-medium tracking-tight flex items-center gap-2">
                <Radio className="w-4 h-4 text-muted-foreground" /> RSS Sources
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