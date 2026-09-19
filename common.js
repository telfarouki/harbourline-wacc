// Harbourline WACC — shared helpers (Supabase client, DOM helper, e-mail code sign-in)
(function () {
  const C = window.WACC_CONFIG || {};
  const configured = /^https:\/\/[a-z0-9-]+\.supabase\.co/i.test(C.SUPABASE_URL || "") && !/YOUR-/.test(C.SUPABASE_ANON_KEY || "YOUR-");
  const sb = configured ? window.supabase.createClient(C.SUPABASE_URL, C.SUPABASE_ANON_KEY) : null;

  // h("div", {class:"x", onclick:fn}, child, "text") — text is always inserted as text, never as HTML
  function h(tag, attrs, ...kids) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else if (k === "class") el.className = v;
      else el.setAttribute(k, v === true ? "" : v);
    }
    for (const kid of kids.flat(Infinity)) {
      if (kid === null || kid === undefined || kid === false) continue;
      el.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
    }
    return el;
  }
  const $ = (id) => document.getElementById(id);
  const safeUrl = (u) => { try { const x = new URL(u); return /^https?:$/.test(x.protocol) ? x.href : null; } catch { return null; } };
  const fmtDate = (s) => { try { return new Date(s).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }); } catch { return s; } };
  function msg(el, kind, text) { el.replaceChildren(text ? h("div", { class: "msg " + kind }, text) : ""); }

  // Renders the sign-in / request-access card into `root`. onSignedIn() is called once a session exists.
  function renderAuth(root, { adminOnly, onSignedIn }) {
    if (!configured) {
      root.replaceChildren(h("div", { class: "card auth" }, h("h2", {}, "Setup needed"),
        h("p", {}, "Open config.js and paste your Supabase Project URL and anon key, then reload this page.")));
      return;
    }
    let mode = "signin", email = "";
    const out = h("div");
    const body = h("div");
    const tabs = h("div", { class: "tabs" + (adminOnly ? " hidden" : "") },
      h("button", { id: "tSign", class: "on", onclick: () => draw("signin") }, "Sign in"),
      h("button", { id: "tReq", onclick: () => draw("request") }, "Request access"));
    root.replaceChildren(h("div", { class: "card auth" }, h("h2", {}, adminOnly ? "Administrator sign-in" : "Access"), tabs, body, out));

    function draw(m) {
      mode = m; msg(out, "", "");
      tabs.children[0].className = m === "request" ? "" : "on";
      tabs.children[1].className = m === "request" ? "on" : "";
      if (m === "signin") {
        const em = h("input", { type: "email", placeholder: "you@company.com", autocomplete: "email", value: email });
        const btn = h("button", { style: "margin-top:14px;width:100%", onclick: async () => {
          email = em.value.trim().toLowerCase();
          if (!email) return;
          btn.disabled = true;
          try {
            const { data: st, error } = await sb.rpc("access_status", { p_email: email });
            if (error) throw error;
            if (adminOnly && st !== "admin") return msg(out, "err", "This e-mail is not an administrator.");
            if (st === "none") return msg(out, "warn", "No access request found for this e-mail. Use “Request access” first.");
            if (st === "pending") return msg(out, "info", "Your request is awaiting the administrator's approval.");
            if (st === "rejected") return msg(out, "err", "Your access request was not approved.");
            const r = await sb.auth.signInWithOtp({ email, options: { shouldCreateUser: true } });
            if (r.error) throw r.error;
            draw("code");
          } catch (e) { msg(out, "err", e.message || String(e)); } finally { btn.disabled = false; }
        } }, "E-mail me a sign-in code");
        body.replaceChildren(h("label", {}, "E-mail"), em, btn);
      } else if (m === "code") {
        const code = h("input", { inputmode: "numeric", autocomplete: "one-time-code", placeholder: "6-digit code", maxlength: "8" });
        const btn = h("button", { style: "margin-top:14px;width:100%", onclick: async () => {
          btn.disabled = true;
          const { error } = await sb.auth.verifyOtp({ email, token: code.value.trim(), type: "email" });
          btn.disabled = false;
          if (error) return msg(out, "err", "Code not accepted: " + error.message);
          onSignedIn();
        } }, "Sign in");
        body.replaceChildren(h("p", {}, "We sent a code to ", h("b", {}, email), ". It can take a minute; check spam too."),
          h("label", {}, "Code"), code, btn,
          h("p", { class: "foot" }, h("button", { class: "link", onclick: () => draw("signin") }, "Use another e-mail")));
        code.focus();
      } else {
        const f = { name: h("input", { autocomplete: "name" }), em: h("input", { type: "email", autocomplete: "email" }),
          co: h("input", { autocomplete: "organization" }), why: h("textarea", { placeholder: "Which projects or countries will you work on?" }) };
        const btn = h("button", { style: "margin-top:14px;width:100%", onclick: async () => {
          btn.disabled = true;
          const { data, error } = await sb.rpc("request_access", { p_email: f.em.value, p_full_name: f.name.value, p_company: f.co.value, p_reason: f.why.value });
          btn.disabled = false;
          if (error) return msg(out, "err", error.message);
          if (data === "approved") { email = f.em.value.trim().toLowerCase(); draw("signin"); return msg(out, "info", "You are already approved — sign in with your e-mail."); }
          body.replaceChildren(h("p", {}, "Thank you. Your request has been sent to the administrator. You will be able to sign in with this e-mail as soon as it is approved."));
        } }, "Send request");
        body.replaceChildren(h("label", {}, "Full name"), f.name, h("label", {}, "Work e-mail"), f.em,
          h("label", {}, "Company ", h("small", {}, "(optional)")), f.co, h("label", {}, "Purpose ", h("small", {}, "(optional)")), f.why, btn);
      }
    }
    draw("signin");
  }

  window.WACC = { sb, h, $, safeUrl, fmtDate, msg, renderAuth, configured, config: C };
})();
