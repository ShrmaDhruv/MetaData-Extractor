import React from "react";

// A static illustration of what the review screen produces. Sample text only.
export default function Specimen() {
  return (
    <figure className="specimen">
      <figcaption>Example record</figcaption>
      <h2 className="specimen__title">A Field Guide to Reading Old Maps with Neural Networks</h2>
      <dl>
        <dt>Authors</dt>
        <dd>Ana Rivera, Tobi Okafor</dd>
        <dt>Affiliations</dt>
        <dd>Department of Geography, University of Example</dd>
        <dt>Emails</dt>
        <dd><span className="highlight">Not found in the paper</span></dd>
        <dt>Keywords</dt>
        <dd>cartography, segmentation, archives</dd>
      </dl>
      <p className="specimen__note">Fields that could not be read are marked so you know where to look.</p>
    </figure>
  );
}
