import React from "react";
import { useUser, UserButton } from "@clerk/clerk-react"; // Import Clerk components

const Hero = () => {
  return (
    <header className='w-full flex justify-center items-center flex-col'>
      <nav className='flex justify-between items-center w-full mb-10 pt-3'>
        <div className='flex items-center gap-4'>
          {/* Clerk User Button */}
          <UserButton afterSignOutUrl="/" />
        </div>
        
        <button
          type='button'
          onClick={() =>
            window.open("https://github.com", "_blank")
          }
          className='rounded-full bg-black text-white py-2 px-4 hover:bg-white hover:text-black'
        >
          GitHub
        </button>
      </nav>

      <h1 className='head_text'>
        LLAMA X<br className='max-md:hidden' />
        <span className='orange_gradient '>THE KILLER</span>
      </h1>
      <h2 className='desc'>
        UPLOAD YOUR FILES IN CSV TO GET STARTED
      </h2>
    </header>
  );
};

export default Hero;
