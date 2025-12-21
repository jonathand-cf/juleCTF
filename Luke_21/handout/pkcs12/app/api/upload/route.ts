import { NextResponse } from 'next/server';
import crypto from 'crypto';
import * as fs from 'fs'; 
const forge = require('node-forge');
const asn1 = forge.asn1 ;
export const runtime = 'nodejs';

function PFXMacDataPresent(obj: any) {
  var p12Asn1 = asn1.fromDer(asn1.toDer(obj).getBytes());
  if(!p12Asn1.value || p12Asn1.value.length != 3) {
    return false ;
  }
  return true ;
}

export async function POST(req: Request) {
  let present: string = "JUL{FAKEFLAG}";
  const filePath: string = 'flag.txt';
  try {
    present = fs.readFileSync(filePath, 'utf-8');
  } catch (error) {
    console.error('Error reading file:', error);                                                                                           
  } 

  try {
    const form = await req.formData();
    const file = form.get('file') as File | null;        
    const password = crypto.randomBytes(32).toString('hex'); // TODO: fix the password part after Christmas. Who needs a password anyways, huh?
    if (!file || !password) {
      return NextResponse.json({ error: 'Missing file or password' }, { status: 400 });
    }
    const buf = Buffer.from(await file.arrayBuffer());

    // Parse PKCS#12; this will throw an error if the password is wrong or MAC is invald
    const p12Asn1 = forge.asn1.fromDer(buf.toString('binary'));
    const p12 = forge.pkcs12.pkcs12FromAsn1(p12Asn1, true, password);

    // To harden our backend we make sure the optional PFX.macData must be present!
    if (!PFXMacDataPresent(p12Asn1)) {
        return NextResponse.json({ error: '🔥 The elves squinted at your file and spotted it — no .macData in the PFX sequence. Almost had us!' }, { status: 400 });   
    }
    
    // PKCS#12 is valid and MAC has been verified!
    // return encrypted present if all checks out!    
    const certBags = p12.getBags({bagType: forge.pki.oids.certBags})[forge.pki.oids.certBags];
    if (certBags && certBags.length > 0) {
      const bag = certBags[0];    
      const issuerCN = bag.cert.issuer.getField('CN');
      const subjectCN = bag.cert.subject.getField('CN');      
      if (issuerCN.value != "santaclaus") {
        return NextResponse.json({ error:  "🎅 Santa does not recognize this issuer. Nice try." }, { status: 400 });        
      }            
      if (subjectCN.value != "wayne") {
        return NextResponse.json({ error: "🎁 Ho ho no! Santa spotted Wayne’s name on this present — back on the shelf it goes!" }, { status: 400 });                
      }
      const encryptedBytes = bag.cert.publicKey.encrypt(present, 'RSA-OAEP', {
        md: forge.md.sha256.create(),
      });
      const encryptedBase64 = forge.util.encode64(encryptedBytes);
      return NextResponse.json({ encrypted: encryptedBase64 });
    } else {
        return NextResponse.json({ error: '📜 Santa checked the package twice, but there’s no certificate inside.' }, { status: 400 });   
    }
  } catch (err: any) {
    return NextResponse.json({ error: 'Santa couldn’t open the file. Either the PKCS#12 is malformed… or the problem isn’t the password or something else malfunctioned. 😿', }, { status: 400 });
  }
}
