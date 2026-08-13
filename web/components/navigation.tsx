import Link from "next/link";

const links = [
  ["Ask", "/"],
  ["Inbox", "/inbox"],
  ["Library", "/library"],
  ["Reviews", "/reviews"],
  ["Roadmaps", "/roadmaps"],
  ["Runs", "/runs"],
  ["Notifications", "/notifications"],
  ["Settings", "/settings"],
] as const;

export function Navigation({ email }: { email: string }) {
  return (
    <aside className="sidebar">
      <Link className="brand" href="/">
        <span className="brand-mark">P</span>
        <span>
          <strong>Paper-List</strong>
          <span>Research OS</span>
        </span>
      </Link>
      <nav className="nav">
        {links.map(([label, href]) => (
          <Link href={href} key={href}>{label}</Link>
        ))}
      </nav>
      <div className="sidebar-foot">{email}<br />Private workspace · public knowledge</div>
    </aside>
  );
}
