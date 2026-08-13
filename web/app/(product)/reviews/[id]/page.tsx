import { notFound } from "next/navigation";
import { ReviewEditor } from "@/components/review-editor";
import { db } from "@/lib/db";

export default async function ReviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const rows = await db()`select rv.*, coalesce(ri.title, rm.title, 'Review') as title from review_items rv left join research_items ri on ri.id=rv.research_item_id left join roadmaps rm on rm.id=rv.roadmap_id where rv.id=${id}`;
  if (!rows[0]) notFound(); const review=rows[0];
  const sections = await db()`select id, section_key, title, generated_markdown, edited_markdown, status, required from review_sections where review_item_id=${id} order by ordinal`;
  return <div className="page"><header className="page-head"><div><div className="eyebrow">{review.review_type} · {review.status}</div><h1>{review.title}</h1><p className="lead">人工编辑是最终权威。发布前会再次检查 required sections、Git base SHA 和 secret patterns。</p></div></header><ReviewEditor reviewId={id} sections={sections as never} /></div>;
}
