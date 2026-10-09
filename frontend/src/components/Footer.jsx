import React from "react";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="wrap site-footer__row">
        <p>Metadata Extractor reads the first page of research papers and leaves the final say to you.</p>
        <nav aria-label="Footer">
          <Link to="/">Extract</Link>
          <Link to="/about">About</Link>
          <Link to="/contact">Contact</Link>
        </nav>
      </div>
    </footer>
  );
}
