import { motion } from "framer-motion";
import Body from "./Body";
import Footer from "./Footer";

export default function HomePage() {
  return (
    <div className="bg-gray-50 text-gray-900">
      
      {/* HERO SECTION */}
      <section className="relative min-h-screen flex flex-col items-center justify-center text-center px-6 overflow-hidden">
        <motion.h1
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          className="text-4xl md:text-6xl font-extrabold bg-gradient-to-r from-indigo-600 via-blue-500 to-cyan-400 bg-clip-text text-transparent"
        >
          MetaData Extractor
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 1 }}
          className="mt-6 max-w-2xl text-lg md:text-xl text-gray-600"
        >
          An intelligent AI system for layout detection and metadata extraction from research papers.
        </motion.p>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{
            delay: 1.2,
            duration: 1,
            repeat: Infinity,
            repeatType: "reverse",
          }}
          className="absolute bottom-10 text-gray-500 animate-bounce"
        >
          ↓ Scroll Down
        </motion.div>
      </section>

      {/* WHY SECTION */}
      <section className="py-20 bg-white px-6 md:px-12">
        <div className="max-w-5xl mx-auto text-center">
          
          <motion.h2
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 1 }}
            viewport={{ once: true }}
            className="text-3xl md:text-4xl font-bold text-gray-800 mb-6"
          >
            Why MetaData Extractor?
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 1 }}
            viewport={{ once: true }}
            className="text-lg text-gray-600 max-w-3xl mx-auto"
          >
            Extracting structured metadata from research papers is essential for 
            automating academic workflows. Traditional OCR tools struggle with complex 
            page layouts, multiple columns, mixed fonts, and dense formatting.
            MetaData Extractor solves this by combining AI-powered layout detection 
            with precise, targeted OCR—making metadata extraction faster, more accurate, 
            and highly reliable.
          </motion.p>

          {/* FEATURES */}
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {[
              {
                title: "Accurate Detection",
                desc: "Identifies title, authors, emails, abstract, and content with exceptional accuracy.",
              },
              {
                title: "AI Powered",
                desc: "Uses the YOLO DocSynth 300K model to understand and segment complex research paper layouts.",
              },
              {
                title: "Time Saving",
                desc: "Extracts structured metadata from the first page in seconds, improving workflow efficiency.",
              },
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: idx * 0.2 }}
                viewport={{ once: true }}
                className="bg-gray-50 rounded-2xl shadow-md p-6 hover:shadow-xl transition"
              >
                <h3 className="text-xl font-semibold text-indigo-600 mb-3">
                  {item.title}
                </h3>
                <p className="text-gray-600">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* UPLOAD SECTION */}
      <section id="upload" className="py-20 px-6 md:px-12">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
          className="max-w-5xl mx-auto"
        >
          <Body />
        </motion.div>        
      </section>
    </div>
  );
}
