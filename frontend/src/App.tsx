import { SignIn, SignedIn, SignedOut } from "@clerk/clerk-react";
import Hero from "./components/Hero";
import Demo from "./components/Demo";
import "./app.css";

function App() {
  return (
    <main>
      <div className='gradient' />

      <div>
        <SignedOut>
          <div className="min-h-screen flex items-center justify-center">
            <SignIn />
          </div>
        </SignedOut>

        <SignedIn>
          <div className="app">
            <Hero />
            <Demo />
          </div>
        </SignedIn>
      </div>
    </main>
  );
}

export default App;
