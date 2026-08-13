import Link from "next/link";
import { ResearchForm } from "@/components/research-form";
import { db } from "@/lib/db";

export default async function AskPage() {
  const [metrics, recent] = await Promise.all([
    db()`select
      (select count(*) from research_items) as items,
      (select count(*) from research_items where reading_status = 'read') as read,
      (select count(*) from review_items where status in ('pending','in_review')) as reviews,
      (select count(*) from roadmaps where status = 'stale') as stale`,
    db()`select id, title, item_type, lifecycle_status, created_at from research_items order by created_at desc limit 5`,
  ]);
  const metric = metrics[0];
  return (
    <div className="page">
      <header className="page-head"><div><div className="eyebrow">Ask · map · understand</div><h1>What are you trying to understand?</h1><p className="lead">从已有知识出发，同时研究全网 primary sources；事实回到证据，推断保持可见。</p></div></header>
      <ResearchForm />
      <section className="section grid grid-4">
        <div className="card card-pad metric"><strong>{metric.items}</strong><span>Research Items</span></div>
        <div className="card card-pad metric"><strong>{metric.read}</strong><span>Read</span></div>
        <div className="card card-pad metric"><strong>{metric.reviews}</strong><span>Awaiting review</span></div>
        <div className="card card-pad metric"><strong>{metric.stale}</strong><span>Stale roadmaps</span></div>
      </section>
      <section className="section"><div className="section-head"><h2>Recently added</h2><Link href="/library">View library →</Link></div><div className="card">
        {recent.length ? recent.map((item) => <Link className="item-row row" href={`/library/${item.id}`} key={item.id}><div><div className="item-title">{item.title}</div><div className="meta"><span>{item.item_type}</span><span>{item.lifecycle_status}</span></div></div><span>→</span></Link>) : <div className="empty">Paste your first paper or research link in Inbox.</div>}
      </div></section>
    </div>
  );
}
