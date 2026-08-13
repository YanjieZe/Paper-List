import { notFound } from "next/navigation";
import { DeepReadButton } from "@/components/deep-read-button";
import { ReadToggle } from "@/components/read-toggle";
import { RelationDecision } from "@/components/relation-decision";
import { db } from "@/lib/db";

export default async function ItemPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const rows = await db()`
    select ri.*, w.slug, w.canonical_title, (select count(*) from document_chunks dc join document_versions dv on dv.id=dc.document_version_id where dv.research_item_id=ri.id) as chunks
    from research_items ri left join works w on w.id=ri.work_id where ri.id=${id}`;
  if (!rows[0]) notFound(); const item = rows[0];
  const sources = await db()`select * from item_sources where research_item_id=${id} order by is_official desc, created_at`;
  const reviews = await db()`select id, status, review_type, created_at from review_items where research_item_id=${id} order by created_at desc`;
  const relations = item.work_id ? await db()`
    select r.id, r.relation_type, r.rationale, r.confidence, r.review_status,
      case when r.source_work_id=${item.work_id} then target.canonical_title else source.canonical_title end as related_title
    from relations r join works source on source.id=r.source_work_id join works target on target.id=r.target_work_id
    where r.source_work_id=${item.work_id} or r.target_work_id=${item.work_id}
    order by r.confidence desc` : [];
  return <div className="page"><header className="page-head"><div><div className="eyebrow">{item.item_type} · {item.lifecycle_status}</div><h1>{item.title}</h1><p className="lead">{item.abstract ?? "No abstract has been extracted yet."}</p></div><ReadToggle itemId={id} initial={item.reading_status} /></header>
    <div className="grid grid-3"><div className="card card-pad metric"><strong>{item.year ?? "—"}</strong><span>Year</span></div><div className="card card-pad metric"><strong>{item.chunks}</strong><span>Evidence chunks</span></div><div className="card card-pad metric"><strong>{reviews.length}</strong><span>Review drafts</span></div></div>
    <section className="section grid grid-2"><div className="card card-pad stack"><h2>Deep reading</h2><p className="lead">生成分层中文讲解，保留 English terminology，并为事实绑定 page/section evidence。</p><DeepReadButton itemId={id} /></div><div className="card card-pad"><h2>Sources</h2><div className="stack"><a href={item.canonical_url} target="_blank">{item.canonical_url} ↗</a>{sources.map((source) => <a href={source.url} target="_blank" key={source.id}>{source.source_type} · {source.url}</a>)}</div></div></section>
    {reviews.length > 0 && <section className="section"><div className="section-head"><h2>Reviews</h2></div><div className="card">{reviews.map((review) => <a className="item-row row" href={`/reviews/${review.id}`} key={review.id}><span>{review.review_type}</span><span className="badge">{review.status}</span></a>)}</div></section>}
    {relations.length > 0 && <section className="section"><div className="section-head"><h2>Relations</h2></div><div className="card">{relations.map((relation) => <article className="item-row" key={relation.id}><div className="row"><strong>{relation.relation_type} · {relation.related_title}</strong><RelationDecision id={relation.id} initial={relation.review_status} /></div><p className="lead">{relation.rationale}</p><div className="meta">confidence {Number(relation.confidence).toFixed(2)}</div></article>)}</div></section>}
  </div>;
}
