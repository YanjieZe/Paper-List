import Link from "next/link";
import { db } from "@/lib/db";
import { formatDate } from "@/lib/format";

export default async function ReviewsPage() {
  const reviews = await db()`
    select rv.id, rv.review_type, rv.status, rv.created_at, coalesce(ri.title, rm.title, 'System conflict') as title,
      count(rs.id) filter (where rs.required and rs.status='pending') as pending
    from review_items rv left join research_items ri on ri.id=rv.research_item_id left join roadmaps rm on rm.id=rv.roadmap_id left join review_sections rs on rs.review_item_id=rv.id
    group by rv.id, ri.title, rm.title order by rv.created_at desc limit 100`;
  return <div className="page"><header className="page-head"><div><div className="eyebrow">Human authority</div><h1>Review</h1><p className="lead">Agent 只能提出 draft；你按章节接受、编辑或退回后，知识才有资格进入 Git。</p></div></header><div className="card">{reviews.length ? reviews.map((review) => <Link className="item-row row" href={`/reviews/${review.id}`} key={review.id}><div><div className="item-title">{review.title}</div><div className="meta"><span>{review.review_type}</span><span>{formatDate(review.created_at)}</span><span>{review.pending} pending</span></div></div><span className={`badge ${review.status === "published" ? "green" : "amber"}`}>{review.status}</span></Link>) : <div className="empty">No review drafts yet.</div>}</div></div>;
}
