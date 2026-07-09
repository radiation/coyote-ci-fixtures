package fixtures.coyote.maven;

import org.apache.commons.lang3.StringUtils;

public final class App {
    private App() {
    }

    public static void main(String[] args) {
        System.out.println(StringUtils.capitalize("maven dependency smoke"));
    }
}
