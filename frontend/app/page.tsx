"use client";
import type { NextPage } from "next";
import ConnectWalletButton from "@/components/wallet-button";

const Home: NextPage = () => {
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Navbar */}
      <nav className="p-6 border-b border-gray-800">
        <div className="container mx-auto flex justify-between items-center">
          <div className="text-2xl font-bold text-blue-500">CryptoX</div>

          <ConnectWalletButton />
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20 text-center">
        <h1 className="text-5xl font-bold mb-6">
          Welcome to the Future of <span className="text-blue-500">Crypto</span>
        </h1>
        <p className="text-gray-400 text-xl mb-8">
          Secure, fast, and decentralized cryptocurrency trading for everyone.
        </p>
        <div className="space-x-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg">
            Get Started
          </button>
          <button className="bg-transparent border border-blue-600 text-blue-500 hover:bg-blue-600 hover:text-white px-8 py-3 rounded-lg">
            Learn More
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-gray-800 py-20">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12">
            Why Choose CryptoX?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-gray-700 p-8 rounded-lg text-center">
              <h3 className="text-xl font-bold mb-4">Secure Transactions</h3>
              <p className="text-gray-400">
                Your assets are protected with state-of-the-art encryption and
                blockchain technology.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-gray-700 p-8 rounded-lg text-center">
              <h3 className="text-xl font-bold mb-4">Fast & Reliable</h3>
              <p className="text-gray-400">
                Experience lightning-fast transactions with minimal fees and no
                downtime.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-gray-700 p-8 rounded-lg text-center">
              <h3 className="text-xl font-bold mb-4">Decentralized</h3>
              <p className="text-gray-400">
                Take control of your finances with a fully decentralized
                platform.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="p-6 border-t border-gray-800">
        <div className="container mx-auto text-center text-gray-400">
          &copy; {new Date().getFullYear()} CryptoX. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

export default Home;
