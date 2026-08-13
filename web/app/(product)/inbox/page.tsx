import Link from "next/link";
import { ImportForm } from "@/components/import-form";
import { db } from "@/lib/db";
import { formatDate } from "@/lib/format";

export default async function InboxPage() {
  const items = await db()`
    select id, title, item_type, lifecycle_status, added_context, canonical_url, created_at
    from research_items where lifecycle_status in ('candidate','triaged','unresolved','failed_retryable')
    order by created_at desc limit 100`;
  const migrationIssues = await db()`select count(*) as count from migration_records where status in ('unresolved','failed_retryable')`;
  return <div className="page"><header className="page-head"><div><div className="eyebrow">Capture</div><h1>Inbox</h1><p className="lead">任何 Research Item 都从这里进入：paper、blog、project、repository、dataset 或 benchmark。</p></div><span className="badge amber">{migrationIssues[0].count} migration issues</span></header>
    <ImportForm />
    <section className="section"><div className="section-head"><h2>Awaiting attention</h2><span className="meta">{items.length} items</span></div><div className="card">{items.length ? items.map((item) => <Link className="item-row row" href={`/library/${item.id}`} key={item.id}><div><div className="item-title">{item.title}</div><div className="meta"><span>{item.item_type}</span><span>{item.lifecycle_status}</span><span>{formatDate(item.created_at)}</span></div>{item.added_context && <div className="meta" style={{ marginTop: 7 }}>{item.added_context}</div>}</div><span>→</span></Link>) : <div className="empty">Inbox is clear.</div>}</div></section>
  </div>;
}
