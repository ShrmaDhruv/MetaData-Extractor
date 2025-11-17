export default function Contact() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-12 text-center">
      
      <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mb-4">
        Contact Us
      </h2>

      <p className="text-gray-600 mb-8">
        Have questions about this project or want to connect with the team?
        Feel free to reach out to any of us!
      </p>

      <div className="flex flex-col md:flex-row items-center justify-center gap-4">
        
        {/* Your GitHub */}
        <a
          href="https://github.com/ShrmaDhruv"
          target="_blank"
          rel="noopener noreferrer"
          className="w-full md:w-auto bg-gray-800 text-white px-6 py-3 rounded-lg shadow-md hover:bg-gray-700 transition"
        >
          Dhruv Sharma — GitHub
        </a>

        {/* Member 2 */}
        <a
          href="https://github.com/Vaibhav121-code"
          target="_blank"
          rel="noopener noreferrer"
          className="w-full md:w-auto bg-gray-800 text-white px-6 py-3 rounded-lg shadow-md hover:bg-gray-700 transition"
        >
          Vaibhav Singh — GitHub
        </a>

        {/* Member 3 */}
        <a
          href="https://github.com/arjunkapoor4"
          target="_blank"
          rel="noopener noreferrer"
          className="w-full md:w-auto bg-gray-800 text-white px-6 py-3 rounded-lg shadow-md hover:bg-gray-700 transition"
        >
          Arjun Kapoor — GitHub
        </a>

      </div>
    </div>
  );
}
