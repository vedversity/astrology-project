import { MuhuratPage, muhuratMetadata } from "@/components/muhurat";

type Props = { params: Promise<{ type: string; year: string }> };

export async function generateMetadata({ params }: Props) {
  const { type, year } = await params;
  return muhuratMetadata("hi", type, year);
}

export default async function Page({ params }: Props) {
  const { type, year } = await params;
  return <MuhuratPage lang="hi" type={type} year={year} />;
}
