"use client";

import { HeroV5 } from "@/components/landing/HeroV5";
import { PainPoints } from "@/components/landing/PainPoints";
import { LiveDemoStrip } from "@/components/landing/LiveDemoStrip";
import { BentoSteps } from "@/components/landing/BentoSteps";
import { SamplesScroll } from "@/components/landing/SamplesScroll";
import { OutputPreview } from "@/components/landing/OutputPreview";
import { TechStack } from "@/components/landing/TechStack";
import { PricingV5 } from "@/components/landing/PricingV5";
import { FinalCTA } from "@/components/landing/FinalCTA";
import { FooterV5 } from "@/components/landing/FooterV5";

export default function LandingPage() {
  return (
    <div className="flex flex-col items-stretch w-full relative">
      <div className="grain-overlay" />
      <HeroV5 />
      <div className="divider-aurora my-2 opacity-60" />
      <PainPoints />
      <LiveDemoStrip />
      <BentoSteps />
      <SamplesScroll />
      <OutputPreview />
      <TechStack />
      <PricingV5 />
      <FinalCTA />
      <FooterV5 />
    </div>
  );
}
