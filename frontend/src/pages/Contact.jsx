import React from "react";

const PEOPLE = [
  { name: "Dhruv Sharma", url: "https://github.com/ShrmaDhruv" },
  { name: "Vaibhav Singh", url: "https://github.com/Vaibhav121-code" },
  { name: "Arjun Kapoor", url: "https://github.com/arjunkapoor4" },
];

export default function Contact() {
  return (
    <article className="wrap prose">
      <h1>Contact</h1>
      <p className="lede">Questions about the project, or a paper it got wrong? Reach the team on GitHub.</p>
      <ul className="people">
        {PEOPLE.map((p) => (
          <li key={p.url}>
            <a href={p.url} target="_blank" rel="noopener noreferrer">
              <span>{p.name}</span>
              <span className="people__host">github.com/{p.url.split("/").pop()}</span>
            </a>
          </li>
        ))}
      </ul>
    </article>
  );
}
