import React from "react";
import { Link, NavLink } from "react-router-dom";

export function Mark() {
  return (
    <svg className="mark" viewBox="0 0 32 32" aria-hidden="true">
      <rect width="32" height="32" rx="6" fill="currentColor" />
      <rect x="8" y="7" width="16" height="3" fill="var(--mark)" />
      <rect x="8" y="13" width="16" height="2.5" fill="#fff" />
      <rect x="8" y="18" width="11" height="2.5" fill="#fff" />
      <rect x="8" y="23" width="14" height="2.5" fill="#fff" />
    </svg>
  );
}

export default function Header() {
  return (
    <header className="site-header">
      <div className="wrap site-header__row">
        <Link to="/" className="brand">
          <Mark />
          <span>Metadata Extractor</span>
        </Link>
        <nav aria-label="Main">
          <NavLink to="/" end>Extract</NavLink>
          <NavLink to="/about">About</NavLink>
          <NavLink to="/contact">Contact</NavLink>
        </nav>
      </div>
    </header>
  );
}
