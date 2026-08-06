import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/PageHeader";
import { Badge } from "@/components/ui/badge";
import { platformApi } from "@/api/platform";

export const Route = createFileRoute("/_app/documents")({ component: DocumentsPage });

function DocumentsPage() {
  const { data: documents = [] } = useQuery({ queryKey: ["documents"], queryFn: platformApi.documents });

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Documents" title="Knowledge documents" description="Uploaded PDFs, DOCX, TXT, Markdown, and JSON files indexed for Copilot retrieval." />
      <Card className="p-6">
        <div className="grid gap-3 md:grid-cols-2">
          {documents.map((document) => (
            <div key={document.id} className="rounded-lg border border-border/60 bg-background/60 p-4">
              <div className="flex items-center justify-between gap-2">
                <div className="font-medium">{document.filename}</div>
                <Badge variant="outline">{document.file_type?.toUpperCase()}</Badge>
              </div>
              <div className="mt-2 text-sm text-muted-foreground">{document.size_bytes} bytes · Indexed {document.indexed_at ?? document.created_at}</div>
            </div>
          ))}
          {!documents.length && <div className="text-sm text-muted-foreground">No documents uploaded yet.</div>}
        </div>
      </Card>
    </div>
  );
}
