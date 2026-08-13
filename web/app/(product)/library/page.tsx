import Link from "next/link";
import { db } from "@/lib/db";

export default async function LibraryPage({ searchParams }: { searchParams: Promise<{ q?: string; type?: string; read?: string }> }) {
  const filters = await searchParams; const query = filters.q?.trim() ?? ""; const type = filters.type ?? ""; const read = filters.read ?? "";
  const items = await db()`
    select id, title, item_type, year, venue, reading_status, lifecycle_status, authors
    from research_items
    where (${query} = '' or title ilike ${`%${query}%`} or coalesce(abstract,'') ilike ${`%${query}%`})
      and (${type} = '' or item_type = ${type}) and (${read} = '' or reading_status = ${read})
    order by year desc nulls last, created_at desc limit 300`;
  return <div className="page"><header className="page-head"><div><div className="eyebrow">Explore</div><h1>Library</h1><p className="lead">统一检索所有 Research Items，同时保留真实类型、来源与阅读状态。</p></div></header>
    <form className="card card-pad grid grid-3" method="get"><div className="field"><label>Search</label><input className="input" name="q" defaultValue={query} placeholder="title, abstract, method…" /></div><div className="field"><label>Type</label><select className="select" name="type" defaultValue={type}><option value="">All types</option>{["paper","blog","article","project","repository","dataset","benchmark","collection"].map((value) => <option key={value}>{value}</option>)}</select></div><div className="field"><label>Reading</label><select className="select" name="read" defaultValue={read}><option value="">All</option><option value="unread">unread</option><option value="read">read</option></select></div><button className="button" style={{ width: "fit-content" }}>Filter</button></form>
    <section className="section"><div className="section-head"><h2>{items.length} results</h2></div><div className="card">{items.map((item) => <Link className="item-row row" href={`/library/${item.id}`} key={item.id}><div><div className="item-title">{item.title}</div><div className="meta"><span>{item.item_type}</span><span>{item.year ?? "year unknown"}</span><span>{item.venue ?? ""}</span><span>{item.reading_status}</span><span>{item.lifecycle_status}</span></div></div><span>→</span></Link>)}</div></section>
  </div>;
}
