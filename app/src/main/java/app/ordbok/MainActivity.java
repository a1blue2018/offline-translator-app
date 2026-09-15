package app.ordbok;

import android.app.Activity;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
  private WebView webView;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    Window window = getWindow();
    if (Build.VERSION.SDK_INT >= 21) {
      window.setStatusBarColor(Color.parseColor("#234037"));
      window.setNavigationBarColor(Color.parseColor("#F3EEE4"));
    }
    if (Build.VERSION.SDK_INT >= 23) {
      window.getDecorView().setSystemUiVisibility(0);
    }

    webView = new WebView(this);
    webView.setBackgroundColor(Color.parseColor("#F3EEE4"));
    webView.setWebViewClient(new WebViewClient());

    WebSettings settings = webView.getSettings();
    settings.setJavaScriptEnabled(true);
    settings.setDomStorageEnabled(true);
    settings.setAllowFileAccess(true);
    settings.setAllowContentAccess(true);
    settings.setDatabaseEnabled(true);
    settings.setUseWideViewPort(true);
    settings.setLoadWithOverviewMode(true);
    settings.setSupportZoom(false);
    settings.setBuiltInZoomControls(false);
    settings.setDisplayZoomControls(false);
    settings.setTextZoom(100);
    settings.setCacheMode(WebSettings.LOAD_NO_CACHE);
    if (Build.VERSION.SDK_INT >= 16) {
      settings.setAllowFileAccessFromFileURLs(true);
      settings.setAllowUniversalAccessFromFileURLs(true);
    }
    if (Build.VERSION.SDK_INT >= 21) {
      settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
    }

    webView.loadUrl("file:///android_asset/www/index.html");
    setContentView(webView);
  }

  @Override
  public void onBackPressed() {
    if (webView != null && webView.canGoBack()) {
      webView.goBack();
      return;
    }
    super.onBackPressed();
  }
}
